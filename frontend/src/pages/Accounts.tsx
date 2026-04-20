import React from "react";
import { motion } from "motion/react";
import { useAccounts } from "@/hooks/useAccounts";
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
import { Plus, Trash2, Wallet, Landmark, CreditCard } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import ResourceFormDialog, { FieldSpec } from "@/components/ResourceFormDialog";

const ACCOUNT_FIELDS: FieldSpec[] = [
  { name: "name", label: "Account Name", type: "text", required: true, placeholder: "e.g. Maybank Savings" },
  { name: "institution", label: "Institution", type: "text", placeholder: "e.g. Maybank" },
  { name: "currency", label: "Currency (ISO code)", type: "text", placeholder: "MYR", defaultValue: "MYR" },
  { name: "account_number", label: "Account Number", type: "text" },
  { name: "description", label: "Description", type: "text" },
  { name: "is_liability", label: "This is a liability (debt)", type: "checkbox" },
];

const AccountIcon = ({ type }: { type?: string }) => {
  switch ((type ?? "").toLowerCase()) {
    case "bank": return <Landmark size={18} />;
    case "broker": return <Wallet size={18} />;
    default: return <CreditCard size={18} />;
  }
};

const Accounts: React.FC = () => {
  const { accounts, isLoading, createAccount, deleteAccount } = useAccounts();

  const confirmDelete = (id: string, name: string) => {
    if (window.confirm(`Delete account "${name}"? This cannot be undone.`)) {
      deleteAccount(id);
    }
  };
  const [open, setOpen] = React.useState(false);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight">Accounts</h1>
          <p className="text-muted-foreground">Manage your bank and brokerage accounts.</p>
        </div>
        <Button
          onClick={() => setOpen(true)}
          className="rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white gap-2 h-11 px-6"
        >
          <Plus size={18} />
          <span className="hidden sm:inline">Add Account</span>
        </Button>
      </div>

      <ResourceFormDialog
        open={open}
        onOpenChange={setOpen}
        title="Add Account"
        description="Create a new bank or brokerage account."
        fields={ACCOUNT_FIELDS}
        submitLabel="Create Account"
        onSubmit={(values: Record<string, any>) => createAccount(values)}
      />

      {/* Desktop Table */}
      <div className="hidden md:block rounded-2xl border bg-card/50 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent border-white/5">
              <TableHead className="w-[300px]">Account Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Currency</TableHead>
              <TableHead className="text-right">Balance</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              [1, 2, 3].map((i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-40" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-12" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-5 w-24 ml-auto" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-5" /></TableCell>
                </TableRow>
              ))
            ) : accounts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-muted-foreground">
                  No accounts found. Add your first account to get started.
                </TableCell>
              </TableRow>
            ) : (
              accounts.map((account) => (
                <TableRow key={account.id} className="hover:bg-white/5 border-white/5">
                  <TableCell className="font-medium flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-accent text-accent-foreground">
                      <AccountIcon type={account.type} />
                    </div>
                    {account.name}
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="rounded-md font-normal">
                      {account.type}
                    </Badge>
                  </TableCell>
                  <TableCell>{account.currency}</TableCell>
                  <TableCell className="text-right font-bold">
                    {(account.balance ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => confirmDelete(account.id, account.name)}
                      title="Delete account"
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
              <CardContent className="p-4 flex items-center gap-4">
                <Skeleton className="h-12 w-12 rounded-xl" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-20" />
                </div>
                <Skeleton className="h-4 w-20" />
              </CardContent>
            </Card>
          ))
        ) : accounts.length === 0 ? (
          <div className="h-32 flex items-center justify-center text-muted-foreground text-sm">
            No accounts found.
          </div>
        ) : (
          accounts.map((account) => (
            <Card key={account.id} className="rounded-2xl border-none bg-card/50">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-accent text-accent-foreground">
                    <AccountIcon type={account.type} />
                  </div>
                  <div>
                    <div className="font-bold">{account.name}</div>
                    <div className="text-xs text-muted-foreground">{account.type} • {account.currency}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-emerald-500">
                    {(account.balance ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
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

export default Accounts;
