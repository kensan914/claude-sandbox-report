import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { Header } from "@/components/features/layout/Header";
import { render } from "../utils";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

describe("Header", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response());
  });

  it("アプリ名が表示される", () => {
    render(<Header user={null} onMenuToggle={vi.fn()} />);
    expect(screen.getByText("営業日報システム")).toBeInTheDocument();
  });

  it("SALES ユーザーの名前とロールバッジが表示される", () => {
    render(
      <Header
        user={{ name: "田中太郎", role: "SALES" }}
        onMenuToggle={vi.fn()}
      />,
    );
    expect(screen.getByText("田中太郎")).toBeInTheDocument();
    expect(screen.getByText("営業")).toBeInTheDocument();
  });

  it("MANAGER ユーザーの名前とロールバッジが表示される", () => {
    render(
      <Header
        user={{ name: "山田部長", role: "MANAGER" }}
        onMenuToggle={vi.fn()}
      />,
    );
    expect(screen.getByText("山田部長")).toBeInTheDocument();
    expect(screen.getByText("マネージャー")).toBeInTheDocument();
  });

  it("ユーザーが null の場合、名前・バッジ・ログアウトが表示されない", () => {
    render(<Header user={null} onMenuToggle={vi.fn()} />);
    expect(screen.queryByLabelText("ログアウト")).not.toBeInTheDocument();
  });

  it("ログアウトボタンクリックで /login へ遷移する", async () => {
    const user = userEvent.setup();
    render(
      <Header
        user={{ name: "田中太郎", role: "SALES" }}
        onMenuToggle={vi.fn()}
      />,
    );
    await user.click(screen.getByLabelText("ログアウト"));
    expect(globalThis.fetch).toHaveBeenCalledWith("/api/v1/auth/logout", {
      method: "POST",
    });
    expect(pushMock).toHaveBeenCalledWith("/login");
  });

  it("メニューボタンクリックで onMenuToggle が呼ばれる", async () => {
    const user = userEvent.setup();
    const onMenuToggle = vi.fn();
    render(
      <Header
        user={{ name: "田中太郎", role: "SALES" }}
        onMenuToggle={onMenuToggle}
      />,
    );
    await user.click(screen.getByLabelText("メニューを開く"));
    expect(onMenuToggle).toHaveBeenCalledTimes(1);
  });
});
