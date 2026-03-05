# Docker helper notes for image build and runtime operations.
This directory intentionally stays small. The primary production Dockerfile is:

- `apps/api/Dockerfile`

It builds the frontend and packages `apps/web/dist` into the API image, so one container serves both API and SPA.
