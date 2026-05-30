# Geospatial AI Autoresearcher

## Running the CesiumJS App

The frontend lives in the [`app/`](app/) directory. It's a Vite + React + TypeScript app powered by CesiumJS.

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- A free [Cesium ion](https://ion.cesium.com/) account and access token

### Setup

1. **Get a Cesium ion token**

   Ask Cory — he can provide a token for you. Alternatively, you can sign in at [ion.cesium.com](https://ion.cesium.com/), go to **Access Tokens**, and copy your default token (or create a new one).

2. **Create your local env file**

   ```sh
   cd app
   cp .env.example .env.local
   ```

   Open `app/.env.local` and replace `PASTE_YOUR_TOKEN_HERE` with your token:

   ```env
   VITE_CESIUM_ION_ACCESS_TOKEN=eyJhbGci...your-token-here
   ```

3. **Install dependencies**

   ```sh
   cd app
   npm install
   ```

4. **Start the dev server**

   ```sh
   npm run dev
   ```

   Open [http://localhost:5173](http://localhost:5173) in your browser. You should see a 3D globe flying to San Francisco with OSM buildings loaded.

### Other commands

| Command | Description |
| --- | --- |
| `npm run dev` | Start dev server with hot reload |
| `npm run build` | Production build (output in `app/dist/`) |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint |
