/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { ThemeProvider } from "@/lib/ThemeContext";
import { Layout } from "@/components/layout/Layout";

// Pages
import Dashboard from "@/pages/Dashboard";
import Accounts from "@/pages/Accounts";
import Assets from "@/pages/Assets";
import Market from "@/pages/Market";
import Transactions from "@/pages/Transactions";
import Income from "@/pages/Income";
import Settings from "@/pages/Settings";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/accounts" element={<Accounts />} />
              <Route path="/assets" element={<Assets />} />
              <Route path="/market" element={<Market />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/income" element={<Income />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
