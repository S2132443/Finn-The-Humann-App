import React from "react";
import { motion } from "motion/react";
import { useDashboard } from "@/hooks/useDashboard";
import { useTransactions } from "@/hooks/useTransactions";
import { useMarket } from "@/hooks/useMarket";
import { NetWorthChart } from "@/components/charts/NetWorthChart";
import { AllocationChart } from "@/components/charts/AllocationChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Briefcase,
  PieChart,
} from "lucide-react";
import type { Transaction, MarketItem } from "@/types/api";
import { Link } from "react-router-dom";

const formatMYR = (n: number | undefined | null) =>
  typeof n === "number"
    ? `RM ${n.toLocaleString("en-MY", { maximumFractionDigits: 2 })}`
    : "RM 0";

const formatPct = (n: number | undefined | null) =>
  typeof n === "number" ? `${n >= 0 ? "+" : ""}${n.toFixed(2)}%` : "—";

const formatDate = (iso: string) => {
  try {
    return new Date(iso).toLocaleDateString("en-MY", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return iso;
  }
};

const KPITile = ({ title, value, change, icon: Icon, isLoading }: any) => (
  <Card className="rounded-2xl border-none bg-card/50 overflow-hidden">
    <CardContent className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-500">
          <Icon size={20} />
        </div>
        {typeof change === "number" && (
          <div
            className={`flex items-center text-xs font-medium ${
              change >= 0 ? "text-emerald-500" : "text-rose-500"
            }`}
          >
            {change >= 0 ? (
              <TrendingUp size={12} className="mr-1" />
            ) : (
              <TrendingDown size={12} className="mr-1" />
            )}
            {Math.abs(change).toFixed(1)}%
          </div>
        )}
      </div>
      {isLoading ? (
        <Skeleton className="h-8 w-24 mb-1" />
      ) : (
        <div className="text-2xl font-bold tracking-tight">{value}</div>
      )}
      <div className="text-xs text-muted-foreground mt-1">{title}</div>
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  const {
    netWorth,
    netWorthHistory,
    allocation,
    assetsCount,
    incomeSummary,
    returnsDailySeries,
    isLoading,
  } = useDashboard();
  const { transactions, isLoading: isTxLoading } = useTransactions();
  const { market, isLoading: isMarketLoading } = useMarket();

  // YTD return: last value of the daily Modified Dietz series (%).
  const ytdReturn =
    returnsDailySeries.length > 0
      ? (returnsDailySeries[returnsDailySeries.length - 1] as any).value ?? null
      : null;

  const recentTransactions: Transaction[] = (transactions as Transaction[])
    .slice()
    .sort((a, b) => (a.date < b.date ? 1 : -1))
    .slice(0, 4);

  const watchlist: MarketItem[] = (market as MarketItem[]).slice(0, 4);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, here's your portfolio overview.
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPITile
          title="Net Worth (MYR)"
          value={formatMYR(netWorth?.total_net_worth)}
          icon={DollarSign}
          isLoading={isLoading}
        />
        <KPITile
          title="YTD Return"
          value={ytdReturn !== null ? formatPct(ytdReturn) : "—"}
          change={ytdReturn ?? undefined}
          icon={TrendingUp}
          isLoading={isLoading}
        />
        <KPITile
          title="Total Income"
          value={formatMYR(incomeSummary?.total_income)}
          icon={Briefcase}
          isLoading={isLoading}
        />
        <KPITile
          title="Asset Count"
          value={assetsCount}
          icon={PieChart}
          isLoading={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <NetWorthChart data={netWorthHistory} />
        </div>
        <div>
          <AllocationChart data={allocation} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="rounded-2xl border-none bg-card/50">
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Recent Transactions
            </CardTitle>
            <Link to="/transactions" className="text-xs font-medium text-emerald-500 hover:underline">
              View all →
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {isTxLoading ? (
                [0, 1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-14 w-full" />
                ))
              ) : recentTransactions.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">
                  No transactions yet.
                </p>
              ) : (
                recentTransactions.map((tx) => (
                  <div
                    key={tx.id}
                    className="flex items-center justify-between py-2 border-b last:border-0 border-white/5"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center">
                        {tx.type === "sell" || tx.type === "withdrawal" ? (
                          <TrendingDown size={18} className="text-rose-500" />
                        ) : (
                          <TrendingUp size={18} className="text-emerald-500" />
                        )}
                      </div>
                      <div>
                        <div className="text-sm font-medium capitalize">
                          {tx.description || tx.type}
                        </div>
                        <div className="text-xs text-muted-foreground capitalize">
                          {tx.type} • {formatDate(tx.date)}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {formatMYR(tx.amount)}
                      </div>
                      {typeof tx.quantity === "number" && (
                        <div className="text-xs text-muted-foreground">
                          {tx.quantity} units
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-none bg-card/50">
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Market Watchlist
            </CardTitle>
            <Link to="/market" className="text-xs font-medium text-emerald-500 hover:underline">
              View all →
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {isMarketLoading ? (
                [0, 1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-14 w-full" />
                ))
              ) : watchlist.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">
                  No symbols tracked. Add one from the Market page.
                </p>
              ) : (
                watchlist.map((item) => (
                  <div
                    key={item.symbol}
                    className="flex items-center justify-between py-2 border-b last:border-0 border-white/5"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center font-bold text-xs">
                        {item.symbol.slice(0, 2)}
                      </div>
                      <div>
                        <div className="text-sm font-medium">{item.symbol}</div>
                        <div className="text-xs text-muted-foreground">
                          {item.name || "Market Price"}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {formatMYR(item.price)}
                      </div>
                      <div
                        className={`text-xs font-medium ${
                          (item.change_percentage_24h ?? 0) >= 0
                            ? "text-emerald-500"
                            : "text-rose-500"
                        }`}
                      >
                        {formatPct(item.change_percentage_24h)}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};

export default Dashboard;
