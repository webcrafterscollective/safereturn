# Frontend Dockerfile for development server and production artifact build.
FROM node:20-alpine AS base
WORKDIR /web

COPY apps/web/package.json apps/web/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY apps/web/ ./

FROM base AS dev
EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "5173"]

FROM base AS build
RUN pnpm build

FROM scratch AS export
COPY --from=build /web/dist /dist
