import React from "react";
import { motion } from "motion/react";
import { useMarket } from "@/hooks/useMarket";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, RefreshCw, TrendingUp, TrendingDown, Star, X } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import ResourceFormDialog, { FieldSpec } from "@/components/ResourceFormDialog";

const SYMBOL_FIELDS: FieldSpec[] = [
  { name: "symbol", label: "Symbol", type: "text", required: true, placeholder: "e.g. AAPL, XBTMYR" },
  { name: "name", label: "Display Name", type: "text", placeholder: "e.g. Apple Inc." },
  {
    name: "source",
    label: "Source",
    type: "select",
    defaultValue: "manual",
    options: [
      { value: "manual", label: "Manual" },
      { value: "yahoo", label: "Yahoo Finance" },
      { value: "luno", label: "LUNO" },
    ],
  },
];

const num = (v: unknown): number => {
  const n = typeof v === "string" ? parseFloat(v) : (v as number);
  return Number.isFinite(n) ? n : 0;
};

const Market: React.FC = () => {
  const { market, isLoading, addToWatchlist, removeFromWatchlist, syncBroker, isSyncing } = useMarket();
  const [addOpen, setAddOpen] = React.useState(false);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight">Market</h1>
          <p className="text-muted-foreground">Real-time market data and watchlist.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={() => syncBroker("luno")}
            disabled={isSyncing}
            variant="outline"
            className="rounded-xl h-11 gap-2 bg-card/50 border-none"
          >
            <RefreshCw size={18} className={isSyncing ? "animate-spin" : ""} />
            Sync LUNO
          </Button>
          <Button
            onClick={() => setAddOpen(true)}
            className="rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white gap-2 h-11 px-6"
          >
            <Plus size={18} />
            Add Symbol
          </Button>
        </div>
      </div>

      <ResourceFormDialog
        open={addOpen}
        onOpenChange={setAddOpen}
        title="Add Symbol to Watchlist"
        fields={SYMBOL_FIELDS}
        submitLabel="Add"
        onSubmit={(values: Record<string, any>) => addToWatchlist(values)}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {isLoading ? (
          [1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i} className="rounded-2xl border-none bg-card/50">
              <CardContent className="p-6 space-y-4">
                <div className="flex justify-between">
                  <Skeleton className="h-6 w-16" />
                  <Skeleton className="h-6 w-6 rounded-full" />
                </div>
                <Skeleton className="h-8 w-32" />
                <Skeleton className="h-4 w-20" />
              </CardContent>
            </Card>
          ))
        ) : market.length === 0 ? (
          <div className="col-span-full h-32 flex items-center justify-center text-muted-foreground">
            No market data available. Add symbols to your watchlist.
          </div>
        ) : (
          market.map((item) => (
            <Card key={item.symbol} className="rounded-2xl border-none bg-card/50 hover:bg-card transition-colors group">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="font-bold text-lg">{item.symbol}</div>
                    <div className="text-xs text-muted-foreground truncate max-w-[120px]">{item.name}</div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFromWatchlist(item.symbol)}
                    title="Remove from watchlist"
                    className="rounded-full text-yellow-500 hover:text-rose-500"
                  >
                    <Star size={18} className="fill-current" />
                    <X size={12} className="absolute -bottom-0.5 -right-0.5 opacity-0 group-hover:opacity-100" />
                  </Button>
                </div>
                
                <div className="space-y-1">
                  <div className="text-2xl font-bold tracking-tight">
                    {num(item.price).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </div>
                  <div className={`flex items-center text-sm font-medium ${num(item.change_percentage_24h) >= 0 ? "text-emerald-500" : "text-rose-500"}`}>
                    {num(item.change_percentage_24h) >= 0 ? <TrendingUp size={14} className="mr-1" /> : <TrendingDown size={14} className="mr-1" />}
                    {Math.abs(num(item.change_percentage_24h)).toFixed(2)}%
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-[10px] text-muted-foreground uppercase tracking-wider">
                  <span>{item.currency || "MYR"}</span>
                  <span>{item.last_updated ? new Date(item.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "—"}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </motion.div>
  );
};

export default Market;
