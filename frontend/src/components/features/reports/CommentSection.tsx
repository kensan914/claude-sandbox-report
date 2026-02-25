"use client";

import { MessageSquare } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useCreateComment } from "@/hooks/useCreateComment";
import type { Schemas } from "@/lib/api-types";

type Comment = Schemas["CommentResponse"];

type CommentSectionProps = {
  reportId: number;
  target: "PROBLEM" | "PLAN";
  comments: Comment[];
  canComment: boolean;
};

function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${month}/${day} ${hours}:${minutes}`;
}

export function CommentSection({
  reportId,
  target,
  comments,
  canComment,
}: CommentSectionProps) {
  const [content, setContent] = useState("");
  const [validationError, setValidationError] = useState("");
  const createComment = useCreateComment(reportId);

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed) {
      setValidationError("コメントを入力してください");
      return;
    }
    setValidationError("");
    createComment.mutate(
      { target, content: trimmed },
      {
        onSuccess: () => {
          setContent("");
        },
      },
    );
  };

  return (
    <div className="mt-3">
      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
        <MessageSquare className="size-4" />
        <span>コメント ({comments.length}件)</span>
      </div>

      {comments.length > 0 && (
        <div className="rounded-lg border divide-y">
          {comments.map((comment) => (
            <div key={comment.id} className="p-3">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                <span className="font-medium text-foreground">
                  {comment.manager.name}
                </span>
                <span>{formatDateTime(comment.created_at)}</span>
              </div>
              <p className="text-sm whitespace-pre-wrap">{comment.content}</p>
            </div>
          ))}
        </div>
      )}

      {canComment && (
        <div className="mt-2 flex gap-2">
          <div className="flex-1">
            <textarea
              value={content}
              onChange={(e) => {
                setContent(e.target.value);
                if (validationError) setValidationError("");
              }}
              placeholder="コメントを入力..."
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 min-h-[2.5rem] resize-none"
              rows={1}
            />
            {validationError && (
              <p className="text-sm text-destructive mt-1">{validationError}</p>
            )}
          </div>
          <Button
            size="sm"
            onClick={handleSubmit}
            disabled={createComment.isPending}
          >
            {createComment.isPending ? "投稿中..." : "投稿"}
          </Button>
        </div>
      )}
    </div>
  );
}
