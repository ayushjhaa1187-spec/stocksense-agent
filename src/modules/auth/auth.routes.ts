import { Router } from "express";
import rateLimit from "express-rate-limit";
import helmet from "helmet";
import { AuthController } from "./auth.controller";
import { AuthService } from "./auth.service";
import { requireAuth } from "./auth.middleware";

const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  standardHeaders: true,
  legacyHeaders: false,
  message: { message: "Too many authentication requests. Please try again later." },
});

export const createAuthRouter = (authController: AuthController, authService: AuthService) => {
  const router = Router();
  const verifyAuth = requireAuth(authService);

  router.use(helmet());
  router.use(authRateLimiter);

  router.post("/login", authController.login);
  router.post("/refresh", authController.refresh);
  router.post("/logout", verifyAuth, authController.logout);
  router.get("/me", verifyAuth, authController.me);

  return router;
};
