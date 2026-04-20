import React from "react";
import { motion } from "motion/react";
import { useAssets } from "@/hooks/useAssets";
import { useAccounts } from "@/hooks/useAccounts";
import ResourceFormDialog, { FieldSpec } from "@/components/ResourceFormDialog";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, RefreshCw, TrendingUp, TrendingDown, Trash2 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

const num = (v: unknown): number => {
  const n = typeof v === "string" ? parseFloat(v) : (v as number);
  return Number.isFinite(n) ? n : 0;
};

const Assets: React.FC = () => {
  const { assets, isLoading, refreshPrices, isRefreshing, createAsset, deleteAsset } = useAssets();
  const confirmDelete = (id: string, name: string) => {
    if (window.confirm(`Delete asset "${name}"?`)) deleteAsset(id);
  };
  const { accounts } = useAccounts();
  const [open, setOpen] = React.useState(false);

  const assetFields: FieldSpec[] = [
    {
      name: "account_id",
      label: "Account",
      type: "select",
      required: true,
      options: accounts.map((a: any) => ({ value: a.id, label: a.name })),
    },
    { name: "name", label: "Name", type: "text", required: true, placeholder: "e.g. Apple Inc." },
    { name: "symbol", label: "Symbol", type: "text", placeholder: "AAPL" },
    { name: "quantity", label: "Quantity", type: "number", defaultValue: 0 },
    { name: "current_price", label: "Current Price", type: "number" },
    { name: "cost_basis", label: "Cost Basis (total)", type: "number" },
    { name: "currency", label: "Currency", type: "text", defaultValue: "MYR" },
    { name: "purchase_date", label: "Purchase Date", type: "date" },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight">Assets</h1>
          <p className="text-muted-foreground">Track your investment portfolio performance.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="icon" 
            onClick={() => refreshPrices()} 
            disabled={isRefreshing}
            className="rounded-xl h-11 w-11"
          >
            <RefreshCw size={18} className={isRefreshing ? "animate-spin" : ""} />
          </Button>
          <Button
            onClick={() => setOpen(true)}
            className="rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white gap-2 h-11 px-6 flex-1 sm:flex-none"
          >
            <Plus size={18} />
            <span>Add Asset</span>
          </Button>
        </div>
      </div>

      <ResourceFormDialog
        open={open}
        onOpenChange={setOpen}
        title="Add Asset"
        description="Record a new holding in one of your accounts."
        fields={assetFields}
        submitLabel="Create Asset"
        onSubmit={(values: Record<string, any>) => createAsset(values)}
      />

      {/* Desktop Table */}
      <div className="hidden md:block rounded-2xl border bg-card/50 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent border-white/5">
              <TableHead>Asset</TableHead>
              <TableHead>Class</TableHead>
              <TableHead className="text-right">Price</TableHead>
              <TableHead className="text-right">Quantity</TableHead>
              <TableHead className="text-right">Market Value</TableHead>
              <TableHead className="text-right">P&L %</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              [1, 2, 3, 4, 5].map((i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-40" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-20 ml-auto" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-16 ml-auto" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-16 ml-auto" /></TableCell>
                  <TableCell></TableCell>
                </TableRow>
              ))
            ) : assets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                  No assets found.
                </TableCell>
              </TableRow>
            ) : (
              assets.map((asset) => (
                <TableRow key={asset.id} className="hover:bg-white/5 border-white/5">
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-bold">{asset.symbol}</span>
                      <span className="text-xs text-muted-foreground">{asset.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="rounded-md font-normal border-white/10">
                      {typeof asset.asset_class === "string" ? asset.asset_class : (asset.asset_class as any)?.name ?? "—"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {num(asset.current_price).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-right">
                    {num(asset.quantity).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right font-bold">
                    RM {num(asset.market_value).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className={`flex items-center justify-end font-medium ${num(asset.pl_percentage) >= 0 ? "text-emerald-500" : "text-rose-500"}`}>
                      {num(asset.pl_percentage) >= 0 ? <TrendingUp size={14} className="mr-1" /> : <TrendingDown size={14} className="mr-1" />}
                      {Math.abs(num(asset.pl_percentage)).toFixed(2)}%
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => confirmDelete(asset.id, asset.name || asset.symbol)}
                      title="Delete asset"
                      className="rounded-full text-muted-foreground hover:text-rose-500"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-4">
        {isLoading ? (
          [1, 2, 3].map((i) => (
            <Card key={i} className="rounded-2xl border-none bg-card/50">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-32" />
                </div>
                <Skeleton className="h-4 w-20" />
              </CardContent>
            </Card>
          ))
        ) : (
          assets.map((asset) => (
            <Card key={asset.id} className="rounded-2xl border-none bg-card/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center font-bold text-xs">
                      {(asset.symbol ?? "?")[0]}
                    </div>
                    <div>
                      <div className="font-bold">{asset.symbol}</div>
                      <div className="text-xs text-muted-foreground">{typeof asset.asset_class === "string" ? asset.asset_class : (asset.asset_class as any)?.name ?? "—"}</div>
                    </div>
                  </div>
                  <div className={`flex items-center font-bold text-sm ${num(asset.pl_percentage) >= 0 ? "text-emerald-500" : "text-rose-500"}`}>
                    {num(asset.pl_percentage) >= 0 ? "+" : "-"}{Math.abs(num(asset.pl_percentage)).toFixed(2)}%
                  </div>
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-white/5">
                  <div>
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Market Value</div>
                    <div className="font-bold">RM {num(asset.market_value).toLocaleString()}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Price</div>
                    <div className="font-medium">{num(asset.current_price).toLocaleString()}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </motion.div>
  );
};

export default Assets;
