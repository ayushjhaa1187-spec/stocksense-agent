import { NextFunction, Response } from "express";
import { AuthService } from "./auth.service";
import { RequestWithUser } from "./auth.types";

const REFRESH_COOKIE_NAME = "refresh_token";
const REFRESH_COOKIE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;

export class AuthController {
  constructor(private readonly authService: AuthService) {}

  login = async (req: RequestWithUser, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { email, password } = req.body;
      const { user, tokens } = await this.authService.login({ email, password });

      res
        .cookie(REFRESH_COOKIE_NAME, tokens.refreshToken, {
          httpOnly: true,
          secure: true,
          sameSite: "strict",
          maxAge: REFRESH_COOKIE_MAX_AGE_MS,
        })
        .status(200)
        .json({
          user,
          accessToken: tokens.accessToken,
        });
    } catch (error) {
      next(error);
    }
  };

  refresh = async (req: RequestWithUser, res: Response, next: NextFunction): Promise<void> => {
    try {
      const tokenFromCookie = req.cookies?.[REFRESH_COOKIE_NAME];
      const tokenFromBody = req.body?.refreshToken;
      const refreshToken = tokenFromCookie ?? tokenFromBody;

      const { accessToken, user } = await this.authService.refresh(refreshToken);
      res.status(200).json({ accessToken, user });
    } catch (error) {
      next(error);
    }
  };

  logout = async (req: RequestWithUser, res: Response, next: NextFunction): Promise<void> => {
    try {
      const tokenFromCookie = req.cookies?.[REFRESH_COOKIE_NAME];
      const tokenFromBody = req.body?.refreshToken;
      const refreshToken = tokenFromCookie ?? tokenFromBody;

      await this.authService.logout(refreshToken);
      res.clearCookie(REFRESH_COOKIE_NAME, {
        httpOnly: true,
        secure: true,
        sameSite: "strict",
      });

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  };

  me = async (req: RequestWithUser, res: Response, next: NextFunction): Promise<void> => {
    try {
      const userId = req.user?.userId;
      if (!userId) {
        res.status(401).json({ message: "Unauthorized" });
        return;
      }

      const user = await this.authService.getCurrentUser(userId);
      if (!user) {
        res.status(404).json({ message: "User not found" });
        return;
      }

      res.status(200).json(user);
    } catch (error) {
      next(error);
    }
  };
}
