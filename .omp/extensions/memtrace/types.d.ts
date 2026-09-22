declare module "@oh-my-pi/pi-coding-agent" {
   export interface ExtensionContext {
      cwd: string;
      sessionManager?: {
         getSessionId?: () => string | undefined;
      };
      ui: {
         notify(message: string, level: "info" | "warning" | "error"): void;
      };
   }

   export interface ExtensionAPI {
      on(
         event: string,
         handler: (event: unknown, context: ExtensionContext) => void | Promise<void>,
      ): void;
      sendMessage(message: {
         customType: string;
         content: string;
         display?: boolean;
      }): Promise<void>;
   }
}

declare module "node:fs" {
   export interface Dirent {
      name: string;
      isDirectory(): boolean;
   }

   export function existsSync(path: string): boolean;
   export function readFileSync(path: string, encoding: "utf-8"): string;
   export function readdirSync(path: string): string[];
   export function readdirSync(path: string, options: { withFileTypes: true }): Dirent[];
}

declare module "node:path" {
   export function join(...parts: string[]): string;
   export function dirname(path: string): string;
   export function isAbsolute(path: string): boolean;
}

declare module "node:child_process" {
   export function spawnSync(
      command: string,
      args: string[],
      options: {
         cwd?: string;
         encoding?: "utf-8";
         env?: Record<string, string | undefined>;
         timeout?: number;
         windowsHide?: boolean;
      },
   ): {
      status: number | null;
      stdout?: string;
      error?: unknown;
   };
}

declare module "node:url" {
   export function fileURLToPath(url: string | URL): string;
}

declare const process: {
   env: Record<string, string | undefined>;
   platform: string;
};
