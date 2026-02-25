import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Sidebar } from "@/components/features/layout/Sidebar";
import { render } from "../utils";

let currentPathname = "/reports";

vi.mock("next/navigation", () => ({
  usePathname: () => currentPathname,
}));

describe("Sidebar", () => {
  it("日報一覧と顧客マスタのリンクが表示される", () => {
    currentPathname = "/reports";
    render(<Sidebar />);
    expect(screen.getByText("日報一覧")).toBeInTheDocument();
    expect(screen.getByText("顧客マスタ")).toBeInTheDocument();
  });

  it("/reports パスで日報一覧がアクティブになる", () => {
    currentPathname = "/reports";
    render(<Sidebar />);
    const link = screen.getByText("日報一覧").closest("a");
    expect(link).toHaveAttribute("href", "/reports");
    expect(link?.className).toContain("bg-accent");
  });

  it("/customers パスで顧客マスタがアクティブになる", () => {
    currentPathname = "/customers";
    render(<Sidebar />);
    const link = screen.getByText("顧客マスタ").closest("a");
    expect(link).toHaveAttribute("href", "/customers");
    expect(link?.className).toContain("bg-accent");
  });

  it("/reports/new などのサブパスでも日報一覧がアクティブになる", () => {
    currentPathname = "/reports/new";
    render(<Sidebar />);
    const link = screen.getByText("日報一覧").closest("a");
    expect(link?.className).toContain("bg-accent");
  });

  it("非アクティブなリンクにはアクティブスタイルが適用されない", () => {
    currentPathname = "/reports";
    render(<Sidebar />);
    const link = screen.getByText("顧客マスタ").closest("a");
    // bg-accent without hover: prefix means it's the active style
    const classes = link?.className.split(" ") ?? [];
    expect(classes).not.toContain("bg-accent");
  });
});
