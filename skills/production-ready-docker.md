# Production-ready Docker

**What this does:** Tells the agent how to write a Dockerfile that's actually shippable — small, secure, fast to build, easy to debug. Covers multi-stage builds, non-root users, healthchecks, and how to handle secrets.

**Why it matters:** Most first-pass Dockerfiles work but are unsafe (run as root), bloated (build tools in the runtime image), or unobservable (no healthcheck). Production needs more than "it builds."

---

## Required practices

### 1. Multi-stage builds

Separate build from runtime. Compilers, dev dependencies, and source archives never end up in the final image.

```dockerfile
# Build stage
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage
FROM node:20-slim AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY package.json ./
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### 2. Non-root user

Never run the application as root. Use the slim/distroless base's built-in user, or create one:

```dockerfile
RUN addgroup -S app && adduser -S app -G app
USER app
```

### 3. Pin base image versions

Never use `:latest`. Pin to a specific tag (`node:20.11-slim`) or a digest for stronger guarantees.

### 4. Use .dockerignore

Exclude `node_modules`, `.git`, `.env`, build artifacts, IDE files. Smaller context = faster builds and no accidental secret leaks.

```
node_modules
.git
.env*
dist
*.log
.vscode
.idea
```

### 5. Layer ordering for cache hits

Copy package manifests first, install deps, *then* copy source. Source changes don't invalidate the dep-install layer.

```dockerfile
COPY package*.json ./   # changes rarely
RUN npm ci              # cached when package.json unchanged
COPY . .                # changes often, but reuses everything above
```

### 6. Healthcheck

Every long-running container needs a healthcheck so orchestrators know if it's actually serving:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

### 7. Secrets via environment, not COPY

Never `COPY .env` into an image. Pass secrets at runtime via `-e` flags, Docker secrets, or the orchestrator's secret store. Anything baked in is leaked forever.

### 8. EXPOSE the port

Document which port the app listens on with `EXPOSE`. It's metadata, not enforcement, but it's the contract for whoever runs your image.

## Verification checklist

Before committing a Dockerfile, confirm:

- [ ] Multi-stage build (or it's a single-stage runtime-only image like Python)
- [ ] No `:latest` tags
- [ ] `.dockerignore` excludes secrets and build artifacts
- [ ] Application runs as a non-root user
- [ ] Healthcheck defined (or there's a deliberate reason not to)
- [ ] Source files copied AFTER dependency installation
- [ ] No secrets in the image (check `docker history <image>`)
- [ ] Image builds and starts successfully (`docker build && docker run`)

Report all eight in your output.
