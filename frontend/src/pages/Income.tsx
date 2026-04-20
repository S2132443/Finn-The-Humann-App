import React from "react";
import { motion } from "motion/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import { useDashboard } from "@/hooks/useDashboard";
import { useAccounts } from "@/hooks/useAccounts";
import ResourceFormDialog, { FieldSpec } from "@/components/ResourceFormDialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, DollarSign } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import type { Income as IncomeRecord } from "@/types/api";

const COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"];

const formatMYR = (n: number | undefined | null) =>
  typeof n === "number"
    ? `RM ${n.toLocaleString("en-MY", { maximumFractionDigits: 2 })}`
    : "RM 0";

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

const Income: React.FC = () => {
  const { incomeSummary, isLoading: isSummaryLoading } = useDashboard();
  const { accounts } = useAccounts();
  const queryClient = useQueryClient();
  const [open, setOpen] = React.useState(false);

  const createIncome = useMutation({
    mutationFn: (data: any) => apiClient.createIncome(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["income"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Income recorded");
    },
    onError: (err: any) => toast.error(err?.message || "Failed to save income"),
  });

  const incomeFields: FieldSpec[] = [
    {
      name: "account_id",
      label: "Account",
      type: "select",
      required: true,
      options: accounts.map((a: any) => ({ value: a.id, label: a.name })),
    },
    {
      name: "income_type",
      label: "Type",
      type: "select",
      required: true,
      options: [
        { value: "dividend", label: "Dividend" },
        { value: "interest", label: "Interest" },
        { value: "rental", label: "Rental" },
        { value: "distribution", label: "Distribution" },
      ],
    },
    { name: "amount", label: "Amount", type: "number", required: true },
    { name: "currency", label: "Currency", type: "text", defaultValue: "MYR" },
    { name: "income_date", label: "Date", type: "date", required: true },
    { name: "description", label: "Description", type: "text" },
    { name: "is_reinvested", label: "Reinvested", type: "checkbox" },
  ];

  const incomeListQuery = useQuery({
    queryKey: ["income"],
    queryFn: () => apiClient.getIncome() as Promise<IncomeRecord[]>,
  });
  const records = (incomeListQuery.data || []).slice().sort(
    (a, b) => (a.date < b.date ? 1 : -1)
  );

  const pieData = incomeSummary?.by_type
    ? Object.entries(incomeSummary.by_type).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight">Income</h1>
          <p className="text-muted-foreground">
            Track your passive income and dividends.
          </p>
        </div>
        <Button
          onClick={() => setOpen(true)}
          className="rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white gap-2 h-11 px-6"
        >
          <Plus size={18} />
          <span className="hidden sm:inline">Add Income</span>
        </Button>
      </div>

      <ResourceFormDialog
        open={open}
        onOpenChange={setOpen}
        title="Record Income"
        fields={incomeFields}
        submitLabel="Save Income"
        onSubmit={(values: Record<string, any>) => createIncome.mutate(values)}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2 rounded-2xl border-none bg-card/50">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Income History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-xl border border-white/5 overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent border-white/5">
                    <TableHead>Date</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {incomeListQuery.isLoading ? (
                    [0, 1, 2, 3].map((i) => (
                      <TableRow key={i}>
                        <TableCell>
                          <Skeleton className="h-5 w-24" />
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-5 w-32" />
                        </TableCell>
                        <TableCell>
                          <Skeleton className="h-5 w-20" />
                        </TableCell>
                        <TableCell className="text-right">
                          <Skeleton className="h-5 w-24 ml-auto" />
                        </TableCell>
                      </TableRow>
                    ))
                  ) : records.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={4}
                        className="text-center text-sm text-muted-foreground py-8"
                      >
                        No income recorded yet.
                      </TableCell>
                    </TableRow>
                  ) : (
                    records.map((r) => (
                      <TableRow
                        key={r.id}
                        className="hover:bg-white/5 border-white/5"
                      >
                        <TableCell className="text-muted-foreground">
                          {formatDate(r.date)}
                        </TableCell>
                        <TableCell className="font-medium">{r.source}</TableCell>
                        <TableCell className="capitalize">{r.type}</TableCell>
                        <TableCell className="text-right font-bold text-emerald-500">
                          {formatMYR(r.amount)}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-none bg-card/50">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Income by Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={
                      pieData.length > 0
                        ? pieData
                        : [{ name: "No Data", value: 1 }]
                    }
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((_entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                        stroke="none"
                      />
                    ))}
                    {pieData.length === 0 && (
                      <Cell fill="hsl(var(--muted))" stroke="none" />
                    )}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      borderColor: "hsl(var(--border))",
                      borderRadius: "12px",
                      fontSize: "12px",
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    iconType="circle"
                    wrapperStyle={{ fontSize: "10px" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between p-4 rounded-xl bg-accent/50">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                    <DollarSign size={18} />
                  </div>
                  <div className="text-sm font-medium">Total YTD</div>
                </div>
                <div className="text-lg font-bold">
                  {isSummaryLoading ? (
                    <Skeleton className="h-6 w-24" />
                  ) : (
                    formatMYR(incomeSummary?.total_income)
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};

export default Income;
