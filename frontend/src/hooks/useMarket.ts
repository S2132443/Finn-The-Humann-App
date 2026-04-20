import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

export const useMarket = () => {
  const queryClient = useQueryClient();

  const marketQuery = useQuery({
    queryKey: ["market"],
    queryFn: () => apiClient.getMarket(),
  });

  const addToWatchlistMutation = useMutation({
    mutationFn: (data: any) => apiClient.addToWatchlist(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["market"] });
      toast.success("Added to watchlist");
    },
  });

  const removeFromWatchlistMutation = useMutation({
    mutationFn: (symbol: string) => apiClient.removeFromWatchlist(symbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["market"] });
      toast.success("Removed from watchlist");
    },
  });

  const syncBrokerMutation = useMutation({
    mutationFn: (provider: string) => apiClient.syncBroker(provider),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["market"] });
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      toast.success("Broker synced");
    },
    onError: (err: any) => toast.error(err?.message || "Sync failed"),
  });

  return {
    market: marketQuery.data || [],
    isLoading: marketQuery.isLoading,
    addToWatchlist: addToWatchlistMutation.mutate,
    removeFromWatchlist: removeFromWatchlistMutation.mutate,
    syncBroker: syncBrokerMutation.mutate,
    isSyncing: syncBrokerMutation.isPending,
  };
};
