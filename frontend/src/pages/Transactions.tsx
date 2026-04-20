import React from "react";
import { motion } from "motion/react";
import { useTransactions } from "@/hooks/useTransactions";
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
import { Plus, ArrowUpRight, ArrowDownLeft, Receipt, Trash2 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

const TransactionIcon = ({ type }: { type: string }) => {
  switch (type) {
    case "buy": return <ArrowDownLeft size={18} className="text-emerald-500" />;
    case "sell": return <ArrowUpRight size={18} className="text-rose-500" />;
    case "dividend": return <Receipt size={18} className="text-blue-500" />;
    default: return <Receipt size={18} />;
  }
};

const Transactions: React.FC = () => {
  const { transactions, isLoading, createTransaction, deleteTransaction } = useTransactions();
  const confirmDelete = (id: string) => {
    if (window.confirm("Delete this transaction?")) deleteTransaction(id);
  };
  const { accounts } = useAccounts();
  const [open, setOpen] = React.useState(false);

  const txFields: FieldSpec[] = [
    {
      name: "account_id",
      label: "Account",
      type: "select",
      required: true,
      options: accounts.map((a: any) => ({ value: a.id, label: a.name })),
    },
    {
      name: "transaction_type",
      label: "Type",
      type: "select",
      required: true,
      options: [
        { value: "deposit", label: "Deposit" },
        { value: "withdrawal", label: "Withdrawal" },
        { value: "transfer", label: "Transfer" },
        { value: "fee", label: "Fee" },
      ],
    },
    { name: "amount", label: "Amount", type: "number", required: true },
    { name: "currency", label: "Currency", type: "text", defaultValue: "MYR" },
    { name: "transaction_date", label: "Date", type: "date", required: true },
    { name: "description", label: "Description", type: "text" },
    { name: "reference", label: "Reference", type: "text" },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight">Transactions</h1>
          <p className="text-muted-foreground">Historical record of all your investment activities.</p>
        </div>
        <Button
          onClick={() => setOpen(true)}
          className="rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white gap-2 h-11 px-6"
        >
          <Plus size={18} />
          <span className="hidden sm:inline">Add Transaction</span>
        </Button>
      </div>

      <ResourceFormDialog
        open={open}
        onOpenChange={setOpen}
        title="Record Transaction"
        fields={txFields}
        submitLabel="Save Transaction"
        onSubmit={(values: Record<string, any>) => createTransaction(values)}
      />

      {/* Desktop Table */}
      <div className="hidden md:block rounded-2xl border bg-card/50 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent border-white/5">
              <TableHead>Date</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Asset</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead className="text-right">Quantity</TableHead>
              <TableHead className="text-right">Price</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              [1, 2, 3, 4, 5].map((i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-32" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-16 ml-auto" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-20 ml-auto" /></TableCell>
                  <TableCell></TableCell>
                </TableRow>
              ))
            ) : transactions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                  No transactions found.
                </TableCell>
              </TableRow>
            ) : (
              transactions.map((tx) => (
                <TableRow key={tx.id} className="hover:bg-white/5 border-white/5">
                  <TableCell className="text-muted-foreground">
                    {new Date(tx.date).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <TransactionIcon type={tx.type} />
                      <span className="capitalize">{tx.type}</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-medium">{tx.asset_id || "Cash"}</TableCell>
                  <TableCell className="text-right font-bold">
                    RM {tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-right">{tx.quantity?.toLocaleString() || "-"}</TableCell>
                  <TableCell className="text-right">{tx.price?.toLocaleString() || "-"}</TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => confirmDelete(tx.id)}
                      title="Delete transaction"
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
                <div className="flex items-center gap-4">
                  <Skeleton className="h-10 w-10 rounded-xl" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                </div>
                <Skeleton className="h-4 w-20" />
              </CardContent>
            </Card>
          ))
        ) : (
          transactions.map((tx) => (
            <Card key={tx.id} className="rounded-2xl border-none bg-card/50">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-accent text-accent-foreground">
                    <TransactionIcon type={tx.type} />
                  </div>
                  <div>
                    <div className="font-bold">{tx.asset_id || "Cash"}</div>
                    <div className="text-xs text-muted-foreground capitalize">{tx.type} • {new Date(tx.date).toLocaleDateString()}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold">
                    RM {tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-[10px] text-muted-foreground">
                    {tx.quantity ? `${tx.quantity} units` : ""}
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

export default Transactions;
