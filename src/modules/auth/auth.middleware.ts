import { NextFunction, Response } from "express";
import { AuthService } from "./auth.service";
import { RequestWithUser } from "./auth.types";

function extractBearerToken(authorizationHeader?: string): string | null {
  if (!authorizationHeader) {
    return null;
  }

  const [scheme, token] = authorizationHeader.split(" ");
  if (scheme !== "Bearer" || !token) {
    return null;
  }

  return token;
}

export const requireAuth = (authService: AuthService) => {
  return (req: RequestWithUser, res: Response, next: NextFunction): void => {
    try {
      const token = extractBearerToken(req.headers.authorization);
      if (!token) {
        res.status(401).json({ message: "Authentication required" });
        return;
      }

      const payload = authService.verifyAccessToken(token);
      req.user = {
        userId: payload.userId,
        role: payload.role,
        permissions: payload.permissions,
      };

      next();
    } catch (_error) {
      res.status(401).json({ message: "Invalid or expired token" });
    }
  };
};

export const requireRole = (role: string) => {
  return (req: RequestWithUser, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({ message: "Authentication required" });
      return;
    }

    if (req.user.role !== role) {
      res.status(403).json({ message: "Insufficient role" });
      return;
    }

    next();
  };
};

export const requirePermission = (permission: string) => {
  return (req: RequestWithUser, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({ message: "Authentication required" });
      return;
    }

    if (!req.user.permissions.includes(permission)) {
      res.status(403).json({ message: "Insufficient permissions" });
      return;
    }

    next();
  };
};
