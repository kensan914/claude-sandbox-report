import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReportStatusBadge } from "@/components/features/reports/ReportStatusBadge";
import { render } from "../utils";

describe("ReportStatusBadge", () => {
  it("DRAFT ステータスで「下書き」と表示される", () => {
    render(<ReportStatusBadge status="DRAFT" />);
    expect(screen.getByText("下書き")).toBeInTheDocument();
  });

  it("SUBMITTED ステータスで「提出済み」と表示される", () => {
    render(<ReportStatusBadge status="SUBMITTED" />);
    expect(screen.getByText("提出済み")).toBeInTheDocument();
  });

  it("REVIEWED ステータスで「確認済み」と表示される", () => {
    render(<ReportStatusBadge status="REVIEWED" />);
    expect(screen.getByText("確認済み")).toBeInTheDocument();
  });

  it("不明なステータスの場合はそのまま表示される", () => {
    render(<ReportStatusBadge status="UNKNOWN" />);
    expect(screen.getByText("UNKNOWN")).toBeInTheDocument();
  });
});
