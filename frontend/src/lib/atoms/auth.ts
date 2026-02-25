import { atom } from "jotai";

export type UserRole = "SALES" | "MANAGER";

export type AuthUser = {
  id: number;
  name: string;
  email: string;
  role: UserRole;
};

export const authUserAtom = atom<AuthUser | null>(null);
