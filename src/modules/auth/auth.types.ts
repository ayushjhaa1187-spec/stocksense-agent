import { Request } from "express";

export type Role = string;

export interface AuthenticatedUser {
  userId: string;
  role: Role;
  permissions: string[];
  email?: string;
  name?: string;
}

export interface TokenPayload {
  userId: string;
  role: Role;
  permissions: string[];
  tokenType: "access" | "refresh";
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface RefreshInput {
  refreshToken?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface RequestWithUser extends Request {
  user?: AuthenticatedUser;
}

export interface PrismaUserRecord {
  id: string;
  email: string;
  password: string;
  role: string;
  permissions?: string[];
  name?: string | null;
}

export interface PrismaLikeClient {
  user: {
    findUnique: (args: { where: { email?: string; id?: string } }) => Promise<PrismaUserRecord | null>;
  };
}
