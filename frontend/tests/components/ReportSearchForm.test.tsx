import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ReportSearchForm } from "@/components/features/reports/ReportSearchForm";
import { render } from "../utils";

vi.mock("@/hooks/useUsers", () => ({
  useUsers: () => ({
    data: {
      data: [
        { id: 1, name: "田中太郎", role: "SALES" },
        { id: 2, name: "鈴木花子", role: "SALES" },
        { id: 3, name: "山田部長", role: "MANAGER" },
      ],
    },
  }),
}));

describe("ReportSearchForm", () => {
  const defaultValues = {
    date_from: "2026-01-01",
    date_to: "2026-01-31",
    salesperson_id: "",
    status: "",
  };

  const defaultProps = {
    values: defaultValues,
    userRole: "SALES" as const,
    onChange: vi.fn(),
    onSearch: vi.fn(),
    onClear: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("報告日、ステータスの検索条件が表示される", () => {
    render(<ReportSearchForm {...defaultProps} />);
    expect(screen.getByLabelText("報告日")).toBeInTheDocument();
    expect(screen.getByLabelText("ステータス")).toBeInTheDocument();
  });

  it("SALES ロールでは担当者フィルタが表示されない", () => {
    render(<ReportSearchForm {...defaultProps} userRole="SALES" />);
    expect(screen.queryByLabelText("担当者")).not.toBeInTheDocument();
  });

  it("MANAGER ロールでは担当者フィルタが表示される", () => {
    render(<ReportSearchForm {...defaultProps} userRole="MANAGER" />);
    expect(screen.getByLabelText("担当者")).toBeInTheDocument();
  });

  it("MANAGER ロールで担当者ドロップダウンに SALES ユーザーのみ表示される", () => {
    render(<ReportSearchForm {...defaultProps} userRole="MANAGER" />);
    const select = screen.getByLabelText("担当者");
    const options = select.querySelectorAll("option");
    // "全件" + 2 SALES users (MANAGER is filtered out)
    expect(options).toHaveLength(3);
    expect(options[1].textContent).toBe("田中太郎");
    expect(options[2].textContent).toBe("鈴木花子");
  });

  it("ステータスのオプションが全て表示される", () => {
    render(<ReportSearchForm {...defaultProps} />);
    const select = screen.getByLabelText("ステータス");
    const options = select.querySelectorAll("option");
    expect(options).toHaveLength(4);
    expect(options[0].textContent).toBe("全件");
    expect(options[1].textContent).toBe("下書き");
    expect(options[2].textContent).toBe("提出済み");
    expect(options[3].textContent).toBe("確認済み");
  });

  it("検索ボタンクリックで onSearch が呼ばれる", async () => {
    const user = userEvent.setup();
    render(<ReportSearchForm {...defaultProps} />);
    await user.click(screen.getByText("検索"));
    expect(defaultProps.onSearch).toHaveBeenCalledTimes(1);
  });

  it("クリアボタンクリックで onClear が呼ばれる", async () => {
    const user = userEvent.setup();
    render(<ReportSearchForm {...defaultProps} />);
    await user.click(screen.getByText("クリア"));
    expect(defaultProps.onClear).toHaveBeenCalledTimes(1);
  });

  it("ステータス変更で onChange が呼ばれる", async () => {
    const user = userEvent.setup();
    render(<ReportSearchForm {...defaultProps} />);
    const select = screen.getByLabelText("ステータス");
    await user.selectOptions(select, "SUBMITTED");
    expect(defaultProps.onChange).toHaveBeenCalledWith({
      ...defaultValues,
      status: "SUBMITTED",
    });
  });
});
