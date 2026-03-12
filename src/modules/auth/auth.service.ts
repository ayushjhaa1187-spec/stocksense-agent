import bcrypt from "bcrypt";
import crypto from "crypto";
import jwt, { SignOptions } from "jsonwebtoken";
import {
  AuthTokens,
  AuthenticatedUser,
  LoginInput,
  PrismaLikeClient,
  PrismaUserRecord,
  TokenPayload,
} from "./auth.types";

const ACCESS_TOKEN_EXPIRES_IN = "15m";
const REFRESH_TOKEN_EXPIRES_IN = "7d";
const BCRYPT_ROUNDS = 12;

// Stores refresh token hashes keyed by token fingerprint for token-level revocation.
const refreshTokenStore = new Map<string, { userId: string; tokenHash: string }>();

export class AuthService {
  constructor(
    private readonly prisma: PrismaLikeClient,
    private readonly accessTokenSecret: string,
    private readonly refreshTokenSecret: string,
  ) {
    if (!this.accessTokenSecret || !this.refreshTokenSecret) {
      throw new Error("JWT secrets are required for auth service");
    }
  }

  async login(input: LoginInput): Promise<{ user: AuthenticatedUser; tokens: AuthTokens }> {
    const normalizedEmail = input.email?.trim().toLowerCase();
    if (!normalizedEmail || !input.password) {
      throw new Error("Email and password are required");
    }

    const user = await this.prisma.user.findUnique({ where: { email: normalizedEmail } });
    if (!user) {
      throw new Error("Invalid credentials");
    }

    const isPasswordValid = await bcrypt.compare(input.password, user.password);
    if (!isPasswordValid) {
      throw new Error("Invalid credentials");
    }

    const authUser = this.buildAuthUser(user);
    const tokens = this.generateTokens(authUser);
    await this.setRefreshToken(authUser.userId, tokens.refreshToken);

    return { user: authUser, tokens };
  }

  async refresh(refreshToken: string): Promise<{ user: AuthenticatedUser; accessToken: string }> {
    if (!refreshToken) {
      throw new Error("Refresh token is required");
    }

    const payload = this.verifyToken(refreshToken, this.refreshTokenSecret, "refresh");
    const isTokenValid = await this.isValidRefreshToken(payload.userId, refreshToken);
    if (!isTokenValid) {
      throw new Error("Invalid refresh token");
    }

    const user = await this.prisma.user.findUnique({ where: { id: payload.userId } });
    if (!user) {
      throw new Error("User not found");
    }

    const authUser = this.buildAuthUser(user);
    const accessToken = this.signToken(
      {
        userId: authUser.userId,
        role: authUser.role,
        permissions: authUser.permissions,
        tokenType: "access",
      },
      this.accessTokenSecret,
      ACCESS_TOKEN_EXPIRES_IN,
    );

    return { user: authUser, accessToken };
  }

  async logout(refreshToken?: string): Promise<void> {
    if (!refreshToken) {
      return;
    }

    const fingerprint = AuthService.generateTokenFingerprint(refreshToken);
    refreshTokenStore.delete(fingerprint);
  }

  async getCurrentUser(userId: string): Promise<AuthenticatedUser | null> {
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    return user ? this.buildAuthUser(user) : null;
  }

  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, BCRYPT_ROUNDS);
  }

  private generateTokens(user: AuthenticatedUser): AuthTokens {
    const accessToken = this.signToken(
      {
        userId: user.userId,
        role: user.role,
        permissions: user.permissions,
        tokenType: "access",
      },
      this.accessTokenSecret,
      ACCESS_TOKEN_EXPIRES_IN,
    );

    const refreshToken = this.signToken(
      {
        userId: user.userId,
        role: user.role,
        permissions: user.permissions,
        tokenType: "refresh",
      },
      this.refreshTokenSecret,
      REFRESH_TOKEN_EXPIRES_IN,
    );

    return { accessToken, refreshToken };
  }

  private signToken(payload: TokenPayload, secret: string, expiresIn: string): string {
    const options: SignOptions = { expiresIn: expiresIn as SignOptions["expiresIn"] };
    return jwt.sign(payload, secret, options);
  }

  verifyAccessToken(token: string): TokenPayload {
    return this.verifyToken(token, this.accessTokenSecret, "access");
  }

  private verifyToken(token: string, secret: string, tokenType: "access" | "refresh"): TokenPayload {
    const payload = jwt.verify(token, secret) as TokenPayload;
    if (!payload || payload.tokenType !== tokenType) {
      throw new Error("Invalid token type");
    }
    return payload;
  }

  private buildAuthUser(user: PrismaUserRecord): AuthenticatedUser {
    return {
      userId: user.id,
      email: user.email,
      name: user.name ?? undefined,
      role: user.role,
      permissions: user.permissions ?? [],
    };
  }

  private async setRefreshToken(userId: string, refreshToken: string): Promise<void> {
    const tokenHash = await bcrypt.hash(refreshToken, BCRYPT_ROUNDS);
    const fingerprint = AuthService.generateTokenFingerprint(refreshToken);
    refreshTokenStore.set(fingerprint, { userId, tokenHash });
  }

  private async isValidRefreshToken(userId: string, refreshToken: string): Promise<boolean> {
    const fingerprint = AuthService.generateTokenFingerprint(refreshToken);
    const savedRecord = refreshTokenStore.get(fingerprint);
    if (!savedRecord || savedRecord.userId !== userId) {
      return false;
    }

    return bcrypt.compare(refreshToken, savedRecord.tokenHash);
  }

  static generateTokenFingerprint(token: string): string {
    return crypto.createHash("sha256").update(token).digest("hex");
  }
}
