export class WorldRendererError extends Error {
  readonly context?: {
    worldId?: string;
    objectId?: string;
    primitiveType?: string;
    componentType?: string;
    frame?: number;
  };

  constructor(
    message: string,
    context?: {
      worldId?: string;
      objectId?: string;
      primitiveType?: string;
      componentType?: string;
      frame?: number;
    },
  ) {
    const typeLabel = context?.componentType ? `component=${context.componentType}` : `primitive=${context?.primitiveType ?? "?"}`;
    const suffix = context
      ? ` [world=${context.worldId ?? "?"}, object=${context.objectId ?? "?"}, ${typeLabel}, frame=${context.frame ?? "?"}]`
      : "";
    super(`${message}${suffix}`);
    this.name = "WorldRendererError";
    this.context = context;
  }
}
