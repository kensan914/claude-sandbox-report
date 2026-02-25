import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { CustomerForm } from "@/components/features/customers/CustomerForm";
import { render } from "../utils";

const createMutateMock = vi.fn();
const updateMutateMock = vi.fn();
const deleteMutateMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/hooks/useCreateCustomer", () => ({
  ApiError: class ApiError extends Error {
    constructor(message: string) {
      super(message);
    }
  },
  useCreateCustomer: () => ({
    mutate: createMutateMock,
    isPending: false,
  }),
}));

vi.mock("@/hooks/useUpdateCustomer", () => ({
  useUpdateCustomer: () => ({
    mutate: updateMutateMock,
    isPending: false,
  }),
}));

vi.mock("@/hooks/useDeleteCustomer", () => ({
  useDeleteCustomer: () => ({
    mutate: deleteMutateMock,
    isPending: false,
  }),
}));

describe("CustomerForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("新規作成モードでフォームが表示される", () => {
    render(<CustomerForm />);
    expect(screen.getByLabelText(/会社名/)).toBeInTheDocument();
    expect(screen.getByLabelText(/担当者名/)).toBeInTheDocument();
    expect(screen.getByLabelText(/住所/)).toBeInTheDocument();
    expect(screen.getByLabelText(/電話番号/)).toBeInTheDocument();
    expect(screen.getByLabelText(/メールアドレス/)).toBeInTheDocument();
    expect(screen.getByText("保存")).toBeInTheDocument();
    expect(screen.getByText("キャンセル")).toBeInTheDocument();
  });

  it("新規作成モードでは削除ボタンが表示されない", () => {
    render(<CustomerForm />);
    expect(screen.queryByText("削除")).not.toBeInTheDocument();
  });

  it("編集モードでは削除ボタンが表示される", () => {
    render(
      <CustomerForm
        initialData={{
          id: 1,
          company_name: "○○株式会社",
          contact_name: "佐藤一郎",
          address: null,
          phone: null,
          email: null,
        }}
      />,
    );
    expect(screen.getByText("削除")).toBeInTheDocument();
  });

  it("編集モードで既存データがプリセットされる", () => {
    render(
      <CustomerForm
        initialData={{
          id: 1,
          company_name: "○○株式会社",
          contact_name: "佐藤一郎",
          address: "東京都",
          phone: "03-1111-2222",
          email: "sato@example.com",
        }}
      />,
    );
    expect(screen.getByDisplayValue("○○株式会社")).toBeInTheDocument();
    expect(screen.getByDisplayValue("佐藤一郎")).toBeInTheDocument();
    expect(screen.getByDisplayValue("東京都")).toBeInTheDocument();
    expect(screen.getByDisplayValue("03-1111-2222")).toBeInTheDocument();
    expect(screen.getByDisplayValue("sato@example.com")).toBeInTheDocument();
  });

  it("会社名未入力で保存するとバリデーションエラーが表示される", async () => {
    const user = userEvent.setup();
    render(<CustomerForm />);
    // 担当者名のみ入力
    await user.type(screen.getByLabelText(/担当者名/), "佐藤");
    await user.click(screen.getByText("保存"));
    await waitFor(() => {
      expect(screen.getByText("会社名を入力してください")).toBeInTheDocument();
    });
    expect(createMutateMock).not.toHaveBeenCalled();
  });

  it("担当者名未入力で保存するとバリデーションエラーが表示される", async () => {
    const user = userEvent.setup();
    render(<CustomerForm />);
    await user.type(screen.getByLabelText(/会社名/), "テスト株式会社");
    await user.click(screen.getByText("保存"));
    await waitFor(() => {
      expect(
        screen.getByText("担当者名を入力してください"),
      ).toBeInTheDocument();
    });
    expect(createMutateMock).not.toHaveBeenCalled();
  });

  it("不正な電話番号形式でバリデーションエラーが表示される", async () => {
    const user = userEvent.setup();
    render(<CustomerForm />);
    await user.type(screen.getByLabelText(/会社名/), "テスト株式会社");
    await user.type(screen.getByLabelText(/担当者名/), "佐藤");
    await user.type(screen.getByLabelText(/電話番号/), "abc");
    await user.click(screen.getByText("保存"));
    await waitFor(() => {
      expect(
        screen.getByText("電話番号の形式で入力してください"),
      ).toBeInTheDocument();
    });
  });

  it("不正なメール形式でバリデーションエラーが表示される", async () => {
    const user = userEvent.setup();
    render(<CustomerForm />);
    await user.type(screen.getByLabelText(/会社名/), "テスト株式会社");
    await user.type(screen.getByLabelText(/担当者名/), "佐藤");
    await user.type(screen.getByLabelText(/メールアドレス/), "invalid");
    await user.click(screen.getByText("保存"));
    await waitFor(() => {
      expect(
        screen.getByText("メール形式で入力してください"),
      ).toBeInTheDocument();
    });
  });

  it("正常入力で保存すると mutate が呼ばれる", async () => {
    const user = userEvent.setup();
    render(<CustomerForm />);
    await user.type(screen.getByLabelText(/会社名/), "テスト株式会社");
    await user.type(screen.getByLabelText(/担当者名/), "佐藤一郎");
    await user.click(screen.getByText("保存"));
    await waitFor(() => {
      expect(createMutateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          company_name: "テスト株式会社",
          contact_name: "佐藤一郎",
        }),
        expect.any(Object),
      );
    });
  });

  it("削除ボタンで confirm ダイアログが表示される", async () => {
    const user = userEvent.setup();
    window.confirm = vi.fn().mockReturnValue(false);
    render(
      <CustomerForm
        initialData={{
          id: 1,
          company_name: "○○株式会社",
          contact_name: "佐藤一郎",
          address: null,
          phone: null,
          email: null,
        }}
      />,
    );
    await user.click(screen.getByText("削除"));
    expect(window.confirm).toHaveBeenCalledWith(
      "この顧客を削除しますか？この操作は取り消せません。",
    );
    expect(deleteMutateMock).not.toHaveBeenCalled();
  });

  it("削除を確認すると deleteMutate が呼ばれる", async () => {
    const user = userEvent.setup();
    window.confirm = vi.fn().mockReturnValue(true);
    render(
      <CustomerForm
        initialData={{
          id: 1,
          company_name: "○○株式会社",
          contact_name: "佐藤一郎",
          address: null,
          phone: null,
          email: null,
        }}
      />,
    );
    await user.click(screen.getByText("削除"));
    expect(deleteMutateMock).toHaveBeenCalled();
  });
});
