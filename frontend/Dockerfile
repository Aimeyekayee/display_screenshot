# Stage 1: Install dependencies only when needed
FROM node:18-alpine AS deps
RUN echo "installing dependencies with node"
RUN node --version
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN yarn --frozen-lockfile --network-timeout 100000000
# Stage 2: Rebuild the source code only when needed
FROM node:18-alpine AS builder
RUN echo "building dependencies with node"
RUN node --version
WORKDIR /app
ENV NEXT_PRIVATE_STANDALONE true
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN yarn run build
# Stage 3: Production image, copy all the files and run next
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3005
CMD ["node", "server.js"]