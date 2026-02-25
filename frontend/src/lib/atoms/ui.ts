import { atom } from "jotai";

export const sidebarOpenAtom = atom<boolean>(true);

/** トースト通知の型 */
export type Toast = {
  id: string;
  type: "success" | "error";
  message: string;
};

/** 表示中のトースト一覧 */
export const toastsAtom = atom<Toast[]>([]);
