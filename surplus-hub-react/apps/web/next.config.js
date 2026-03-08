/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async redirects() {
    return [
      {
        source: "/materials/:id",
        destination: "/material/:id",
        permanent: true,
      },
    ];
  },
  transpilePackages: ["@repo/ui", "@repo/core", "nativewind"],
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
      },
    ],
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      "react-native$": "react-native-web",
    };
    
    // Explicitly map react-native to react-native-web
    config.resolve.alias["react-native"] = "react-native-web";

    config.resolve.extensions = [
      ".web.tsx",
      ".web.ts",
      ".web.jsx",
      ".web.js",
      ...config.resolve.extensions,
    ];

    // Important: Avoid webpack trying to bundle native modules
    config.resolve.fallback = {
      ...config.resolve.fallback,
      "react-native": false,
    };

    return config;
  },
};

export default nextConfig;
