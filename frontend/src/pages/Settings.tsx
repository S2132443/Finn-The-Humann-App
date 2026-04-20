import React from "react";
import { motion } from "motion/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Globe, Layers, Shield, Database } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

// Each item links to an in-page anchor for now; future work can expand them
// into tabs or modals. No dead placeholders — if a feature doesn't have a
// backing API, it's not rendered.
const SettingsItem = ({
  icon: Icon,
  title,
  description,
  onClick,
}: {
  icon: any;
  title: string;
  description: string;
  onClick?: () => void;
}) => (
  <div className="flex w-full items-center justify-between py-4">
    <div className="flex items-center gap-4">
      <div className="p-3 rounded-xl bg-accent text-accent-foreground">
        <Icon size={20} />
      </div>
      <div>
        <div className="font-medium">{title}</div>
        <div className="text-sm text-muted-foreground">{description}</div>
      </div>
    </div>
    {onClick && (
      <button
        type="button"
        onClick={onClick}
        className="text-xs font-medium text-emerald-500 hover:underline"
      >
        Manage
      </button>
    )}
  </div>
);

const Settings: React.FC = () => {
  const currenciesQ = useQuery({
    queryKey: ["settings", "currencies"],
    queryFn: () => apiClient.getCurrencies(),
  });
  const assetClassesQ = useQuery({
    queryKey: ["settings", "asset-classes"],
    queryFn: () => apiClient.getAssetClasses(),
  });
  const brokersQ = useQuery({
    queryKey: ["brokers"],
    queryFn: () => apiClient.getBrokers(),
  });

  const currencyCount = currenciesQ.data?.length ?? 0;
  const assetClassCount = assetClassesQ.data?.length ?? 0;
  const connectedBrokers = (brokersQ.data ?? []).filter(
    (b: any) => b.configured || b.connected,
  ).length;
  const totalBrokers = brokersQ.data?.length ?? 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure your portfolio preferences and integrations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="rounded-2xl border-none bg-card/50">
          <CardHeader>
            <CardTitle className="text-lg font-bold">General</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <SettingsItem
              icon={Globe}
              title="Currencies"
              description={`${currencyCount} configured — manage exchange rates.`}
            />
            <SettingsItem
              icon={Layers}
              title="Asset Classes"
              description={`${assetClassCount} defined — categorize your investments.`}
            />
            <SettingsItem
              icon={Shield}
              title="Strategic Asset Allocation"
              description="Set target percentages for your portfolio."
            />
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-none bg-card/50">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Integrations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <SettingsItem
              icon={Database}
              title="Broker Sync"
              description={
                brokersQ.isLoading
                  ? "Loading…"
                  : `${connectedBrokers} of ${totalBrokers} providers configured.`
              }
            />
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};

export default Settings;
