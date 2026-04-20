import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

export const useSettings = () => {
  const queryClient = useQueryClient();

  const assetClassesQuery = useQuery({
    queryKey: ["settings", "asset-classes"],
    queryFn: () => apiClient.getAssetClasses(),
  });

  const currenciesQuery = useQuery({
    queryKey: ["settings", "currencies"],
    queryFn: () => apiClient.getCurrencies(),
  });

  const updateCurrenciesMutation = useMutation({
    mutationFn: (data: any) => apiClient.updateCurrencies(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings", "currencies"] });
      toast.success("Currencies updated successfully");
    },
  });

  return {
    assetClasses: assetClassesQuery.data || [],
    currencies: currenciesQuery.data || [],
    isLoading: assetClassesQuery.isLoading || currenciesQuery.isLoading,
    updateCurrencies: updateCurrenciesMutation.mutate,
  };
};
