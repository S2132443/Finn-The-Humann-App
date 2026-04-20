import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

export const useAssets = () => {
  const queryClient = useQueryClient();

  const assetsQuery = useQuery({
    queryKey: ["assets"],
    queryFn: () => apiClient.getAssets(),
  });

  const createAssetMutation = useMutation({
    mutationFn: (data: any) => apiClient.createAsset(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      toast.success("Asset added successfully");
    },
  });

  const updateAssetMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => apiClient.updateAsset(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      toast.success("Asset updated successfully");
    },
  });

  const bulkUpdateAssetsMutation = useMutation({
    mutationFn: (data: any) => apiClient.bulkUpdateAssets(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      toast.success("Assets updated successfully");
    },
  });

  const deleteAssetMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteAsset(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      toast.success("Asset removed successfully");
    },
  });

  const refreshPricesMutation = useMutation({
    mutationFn: () => apiClient.refreshPrices(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      toast.success("Prices refreshed successfully");
    },
  });

  return {
    assets: assetsQuery.data || [],
    isLoading: assetsQuery.isLoading,
    createAsset: createAssetMutation.mutate,
    updateAsset: updateAssetMutation.mutate,
    bulkUpdateAssets: bulkUpdateAssetsMutation.mutate,
    deleteAsset: deleteAssetMutation.mutate,
    refreshPrices: refreshPricesMutation.mutate,
    isRefreshing: refreshPricesMutation.isPending,
  };
};
