import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { CommentSection } from "@/components/features/reports/CommentSection";
import { render } from "../utils";

const mutateMock = vi.fn();

vi.mock("@/hooks/useCreateComment", () => ({
  useCreateComment: () => ({
    mutate: mutateMock,
    isPending: false,
  }),
}));

const mockComments = [
  {
    id: 1,
    target: "PROBLEM" as const,
    content: "確認しました",
    manager: { id: 3, name: "山田部長" },
    created_at: "2026-01-15T10:30:00",
  },
  {
    id: 2,
    target: "PROBLEM" as const,
    content: "対応お願いします",
    manager: { id: 3, name: "山田部長" },
    created_at: "2026-01-15T14:00:00",
  },
];

describe("CommentSection", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("コメント件数が表示される", () => {
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={mockComments}
        canComment={false}
      />,
    );
    expect(screen.getByText("コメント (2件)")).toBeInTheDocument();
  });

  it("コメントの内容・投稿者名が表示される", () => {
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={mockComments}
        canComment={false}
      />,
    );
    expect(screen.getByText("確認しました")).toBeInTheDocument();
    expect(screen.getByText("対応お願いします")).toBeInTheDocument();
    expect(screen.getAllByText("山田部長")).toHaveLength(2);
  });

  it("コメント0件の場合、件数が0と表示される", () => {
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={[]}
        canComment={false}
      />,
    );
    expect(screen.getByText("コメント (0件)")).toBeInTheDocument();
  });

  it("canComment=false の場合、入力欄が表示されない", () => {
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={[]}
        canComment={false}
      />,
    );
    expect(
      screen.queryByPlaceholderText("コメントを入力..."),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("投稿")).not.toBeInTheDocument();
  });

  it("canComment=true の場合、入力欄と投稿ボタンが表示される", () => {
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={[]}
        canComment={true}
      />,
    );
    expect(
      screen.getByPlaceholderText("コメントを入力..."),
    ).toBeInTheDocument();
    expect(screen.getByText("投稿")).toBeInTheDocument();
  });

  it("空のコメントで投稿するとバリデーションエラーが表示される", async () => {
    const user = userEvent.setup();
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={[]}
        canComment={true}
      />,
    );
    await user.click(screen.getByText("投稿"));
    expect(
      screen.getByText("コメントを入力してください"),
    ).toBeInTheDocument();
    expect(mutateMock).not.toHaveBeenCalled();
  });

  it("コメントを入力して投稿すると mutate が呼ばれる", async () => {
    const user = userEvent.setup();
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={[]}
        canComment={true}
      />,
    );
    const textarea = screen.getByPlaceholderText("コメントを入力...");
    await user.type(textarea, "テストコメント");
    await user.click(screen.getByText("投稿"));
    expect(mutateMock).toHaveBeenCalledWith(
      { target: "PROBLEM", content: "テストコメント" },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
  });

  it("投稿成功時にテキストエリアがクリアされる", async () => {
    const user = userEvent.setup();
    mutateMock.mockImplementation((_data: unknown, options: { onSuccess?: () => void }) => {
      options.onSuccess?.();
    });
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={[]}
        canComment={true}
      />,
    );
    const textarea = screen.getByPlaceholderText("コメントを入力...");
    await user.type(textarea, "テストコメント");
    await user.click(screen.getByText("投稿"));
    expect(textarea).toHaveValue("");
  });

  it("バリデーションエラーは入力開始で消える", async () => {
    const user = userEvent.setup();
    render(
      <CommentSection
        reportId={1}
        target="PROBLEM"
        comments={[]}
        canComment={true}
      />,
    );
    await user.click(screen.getByText("投稿"));
    expect(
      screen.getByText("コメントを入力してください"),
    ).toBeInTheDocument();
    const textarea = screen.getByPlaceholderText("コメントを入力...");
    await user.type(textarea, "a");
    expect(
      screen.queryByText("コメントを入力してください"),
    ).not.toBeInTheDocument();
  });
});
