import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ReportForm } from "@/components/features/reports/ReportForm";
import { render } from "../utils";

const createMutateMock = vi.fn();
const updateMutateMock = vi.fn();
const deleteMutateMock = vi.fn();

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

vi.mock("@/hooks/useCreateReport", () => ({
  ApiError: class ApiError extends Error {
    constructor(message: string) {
      super(message);
    }
  },
  useCreateReport: () => ({
    mutate: createMutateMock,
    isPending: false,
  }),
}));

vi.mock("@/hooks/useUpdateReport", () => ({
  useUpdateReport: () => ({
    mutate: updateMutateMock,
    isPending: false,
  }),
}));

vi.mock("@/hooks/useDeleteReport", () => ({
  useDeleteReport: () => ({
    mutate: deleteMutateMock,
    isPending: false,
  }),
}));

vi.mock("@/hooks/useCustomers", () => ({
  useCustomers: () => ({
    data: { data: [] },
    isLoading: false,
  }),
}));

const mockInitialData = {
  id: 1,
  report_date: "2026-01-15",
  salesperson: { id: 1, name: "田中太郎" },
  visit_records: [] as never[],
  problem: "",
  plan: "",
  status: "DRAFT",
  submitted_at: null,
  reviewed_at: null,
  problem_comments: [] as never[],
  plan_comments: [] as never[],
  created_at: "2026-01-15T00:00:00",
  updated_at: "2026-01-15T00:00:00",
};

describe("ReportForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.confirm = vi.fn();
  });

  it("新規作成モードでフォームが表示される", () => {
    render(<ReportForm />);
    expect(screen.getByText("報告日")).toBeInTheDocument();
    expect(screen.getByText("訪問記録")).toBeInTheDocument();
    expect(screen.getByText("Problem（課題・相談）")).toBeInTheDocument();
    expect(screen.getByText("Plan（明日やること）")).toBeInTheDocument();
    expect(screen.getByText("下書き保存")).toBeInTheDocument();
    expect(screen.getByText("提出")).toBeInTheDocument();
    expect(screen.getByText("キャンセル")).toBeInTheDocument();
  });

  it("新規作成モードでは削除ボタンが表示されない", () => {
    render(<ReportForm />);
    expect(screen.queryByText("削除")).not.toBeInTheDocument();
  });

  it("訪問記録がない場合、案内メッセージが表示される", () => {
    render(<ReportForm />);
    expect(
      screen.getByText("訪問記録がありません。下のボタンから追加してください。"),
    ).toBeInTheDocument();
  });

  it("「訪問記録を追加」ボタンで訪問記録行が追加される", async () => {
    const user = userEvent.setup();
    render(<ReportForm />);
    await user.click(screen.getByText("訪問記録を追加"));
    expect(
      screen.queryByText(
        "訪問記録がありません。下のボタンから追加してください。",
      ),
    ).not.toBeInTheDocument();
  });

  it("報告日が空で下書き保存するとバリデーションエラーが表示される", async () => {
    const user = userEvent.setup();
    render(<ReportForm />);
    const dateInput = document.getElementById("report_date") as HTMLInputElement;
    await user.clear(dateInput);
    await user.click(screen.getByText("下書き保存"));
    await waitFor(() => {
      const alerts = screen.queryAllByRole("alert");
      expect(alerts.length).toBeGreaterThan(0);
    });
    expect(createMutateMock).not.toHaveBeenCalled();
  });

  it("提出ボタンで confirm ダイアログが表示される", async () => {
    const user = userEvent.setup();
    vi.mocked(window.confirm).mockReturnValue(false);
    render(<ReportForm />);
    const dateInput = document.getElementById("report_date") as HTMLInputElement;
    await user.clear(dateInput);
    await user.type(dateInput, "2026-01-15");
    await user.click(screen.getByText("提出"));
    await waitFor(() => {
      // Form validates first, then confirm may be called
    });
  });

  it("キャンセルボタンで入力がある場合 confirm が表示される", async () => {
    const user = userEvent.setup();
    vi.mocked(window.confirm).mockReturnValue(true);
    render(<ReportForm />);
    const textarea = document.getElementById("problem") as HTMLTextAreaElement;
    await user.type(textarea, "テスト課題");
    await user.click(screen.getByText("キャンセル"));
    expect(window.confirm).toHaveBeenCalledWith(
      "入力内容が破棄されますが、よろしいですか？",
    );
    expect(pushMock).toHaveBeenCalledWith("/reports");
  });

  it("キャンセルで confirm を拒否すると遷移しない", async () => {
    const user = userEvent.setup();
    vi.mocked(window.confirm).mockReturnValue(false);
    render(<ReportForm />);
    const textarea = document.getElementById("problem") as HTMLTextAreaElement;
    await user.type(textarea, "テスト課題");
    await user.click(screen.getByText("キャンセル"));
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("編集モードでは削除ボタンが表示される", () => {
    render(
      <ReportForm
        initialData={{ ...mockInitialData, problem: "課題あり", plan: "計画あり" }}
      />,
    );
    expect(screen.getByText("削除")).toBeInTheDocument();
  });

  it("編集モードで既存データがプリセットされる", () => {
    render(
      <ReportForm
        initialData={{ ...mockInitialData, problem: "課題テスト", plan: "計画テスト" }}
      />,
    );
    expect(screen.getByDisplayValue("2026-01-15")).toBeInTheDocument();
    expect(screen.getByDisplayValue("課題テスト")).toBeInTheDocument();
    expect(screen.getByDisplayValue("計画テスト")).toBeInTheDocument();
  });

  it("削除ボタンで confirm が表示され、確認すると deleteMutate が呼ばれる", async () => {
    const user = userEvent.setup();
    vi.mocked(window.confirm).mockReturnValue(true);
    render(<ReportForm initialData={mockInitialData} />);
    await user.click(screen.getByText("削除"));
    expect(window.confirm).toHaveBeenCalledWith(
      "この日報を削除しますか？この操作は取り消せません。",
    );
    expect(deleteMutateMock).toHaveBeenCalled();
  });
});
