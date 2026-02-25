const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: { field: string; message: string }[],
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new ApiError(401, "UNAUTHORIZED", "認証が必要です");
    }

    const body = await response.json().catch(() => null);
    const error = body?.error;
    throw new ApiError(
      response.status,
      error?.code ?? "UNKNOWN_ERROR",
      error?.message ?? "エラーが発生しました",
      error?.details,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

type RequestOptions = Omit<RequestInit, "body"> & {
  params?: Record<string, string | number | undefined>;
  body?: unknown;
};

function buildUrl(
  path: string,
  params?: Record<string, string | number | undefined>,
): string {
  const url = new URL(`/api/v1${path}`, BASE_URL);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

export const apiClient = {
  async get<T>(path: string, options?: RequestOptions): Promise<T> {
    const { params, body: _, ...init } = options ?? {};
    const response = await fetch(buildUrl(path, params), {
      ...init,
      method: "GET",
      credentials: "include",
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, options?: RequestOptions): Promise<T> {
    const { params, body, ...init } = options ?? {};
    const response = await fetch(buildUrl(path, params), {
      ...init,
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, options?: RequestOptions): Promise<T> {
    const { params, body, ...init } = options ?? {};
    const response = await fetch(buildUrl(path, params), {
      ...init,
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async patch<T>(path: string, options?: RequestOptions): Promise<T> {
    const { params, body, ...init } = options ?? {};
    const response = await fetch(buildUrl(path, params), {
      ...init,
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string, options?: RequestOptions): Promise<T> {
    const { params, body: _, ...init } = options ?? {};
    const response = await fetch(buildUrl(path, params), {
      ...init,
      method: "DELETE",
      credentials: "include",
    });
    return handleResponse<T>(response);
  },
};
