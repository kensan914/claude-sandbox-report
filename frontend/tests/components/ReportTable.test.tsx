import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ReportTable } from "@/components/features/reports/ReportTable";
import { render } from "../utils";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

const mockReports = [
  {
    id: 1,
    report_date: "2026-01-15",
    salesperson: { id: 1, name: "田中太郎" },
    visit_count: 3,
    status: "DRAFT",
    submitted_at: null,
  },
  {
    id: 2,
    report_date: "2026-01-14",
    salesperson: { id: 1, name: "田中太郎" },
    visit_count: 2,
    status: "SUBMITTED",
    submitted_at: "2026-01-14T17:30:00",
  },
  {
    id: 3,
    report_date: "2026-01-13",
    salesperson: { id: 2, name: "鈴木花子" },
    visit_count: 1,
    status: "REVIEWED",
    submitted_at: "2026-01-13T16:00:00",
  },
];

describe("ReportTable", () => {
  const defaultProps = {
    reports: mockReports,
    isLoading: false,
    sortConfig: { sort: "report_date", order: "desc" },
    onSort: vi.fn(),
    pageOffset: 0,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("日報一覧が表示される", () => {
    render(<ReportTable {...defaultProps} />);
    expect(screen.getAllByText("田中太郎").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("鈴木花子")).toBeInTheDocument();
  });

  it("ステータスバッジが正しく表示される", () => {
    render(<ReportTable {...defaultProps} />);
    expect(screen.getByText("下書き")).toBeInTheDocument();
    expect(screen.getByText("提出済み")).toBeInTheDocument();
    expect(screen.getByText("確認済み")).toBeInTheDocument();
  });

  it("行番号が pageOffset を加算して表示される", () => {
    render(<ReportTable {...defaultProps} pageOffset={20} />);
    expect(screen.getByText("21")).toBeInTheDocument();
    expect(screen.getByText("22")).toBeInTheDocument();
    expect(screen.getByText("23")).toBeInTheDocument();
  });

  it("訪問件数が表示される", () => {
    render(<ReportTable {...defaultProps} />);
    // Check that visit counts appear in the table cells
    const rows = screen.getAllByRole("row");
    // Row 1 (first data row) should have visit_count=3
    expect(rows[1]).toHaveTextContent("3");
    // Row 2 should have visit_count=2
    expect(rows[2]).toHaveTextContent("2");
  });

  it("提出日時が null の場合は — が表示される", () => {
    render(<ReportTable {...defaultProps} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("行クリックで日報詳細画面に遷移する", async () => {
    const user = userEvent.setup();
    render(<ReportTable {...defaultProps} />);
    const rows = screen.getAllByRole("row");
    // rows[0] is thead, rows[1] is first data row (id=1)
    await user.click(rows[1]);
    expect(pushMock).toHaveBeenCalledWith("/reports/1");
  });

  it("ソートボタンクリックで onSort が呼ばれる", async () => {
    const user = userEvent.setup();
    const onSort = vi.fn();
    render(<ReportTable {...defaultProps} onSort={onSort} />);
    await user.click(screen.getByText("担当者"));
    expect(onSort).toHaveBeenCalledWith("salesperson_name");
  });

  it("isLoading=true でスケルトンが表示される", () => {
    render(<ReportTable {...defaultProps} reports={[]} isLoading={true} />);
    // 5 skeleton rows should be rendered
    const skeletonCells = document.querySelectorAll(".animate-pulse");
    expect(skeletonCells.length).toBe(5);
  });

  it("空の配列で「日報が見つかりません」が表示される", () => {
    render(<ReportTable {...defaultProps} reports={[]} isLoading={false} />);
    expect(screen.getByText("日報が見つかりません")).toBeInTheDocument();
  });

  it("全てのソートカラムヘッダーが表示される", () => {
    render(<ReportTable {...defaultProps} />);
    expect(screen.getByText("報告日")).toBeInTheDocument();
    expect(screen.getByText("担当者")).toBeInTheDocument();
    expect(screen.getByText("訪問件数")).toBeInTheDocument();
    expect(screen.getByText("ステータス")).toBeInTheDocument();
    expect(screen.getByText("提出日時")).toBeInTheDocument();
  });
});
