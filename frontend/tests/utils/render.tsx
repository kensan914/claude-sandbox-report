import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type RenderOptions, render } from "@testing-library/react";
import { createStore, Provider as JotaiProvider } from "jotai";
import type { ReactElement, ReactNode } from "react";
import { type AuthUser, authUserAtom } from "@/lib/atoms";

type CustomRenderOptions = RenderOptions & {
  authUser?: AuthUser | null;
};

function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

function createWrapper(options: CustomRenderOptions = {}) {
  const { authUser = null } = options;
  const queryClient = createTestQueryClient();
  const store = createStore();

  if (authUser) {
    store.set(authUserAtom, authUser);
  }

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <JotaiProvider store={store}>{children}</JotaiProvider>
      </QueryClientProvider>
    );
  };
}

function customRender(ui: ReactElement, options: CustomRenderOptions = {}) {
  const { authUser, ...renderOptions } = options;
  return render(ui, {
    wrapper: createWrapper({ authUser }),
    ...renderOptions,
  });
}

export { customRender as render, createTestQueryClient };
