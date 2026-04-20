import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

export const useDashboard = () => {
  const netWorthQuery = useQuery({
    queryKey: ["networth"],
    queryFn: () => apiClient.getNetWorth(),
  });

  const netWorthHistoryQuery = useQuery({
    queryKey: ["networth", "history"],
    queryFn: () => apiClient.getNetWorthHistory(),
  });

  const allocationQuery = useQuery({
    queryKey: ["allocation"],
    queryFn: () => apiClient.getAllocation(),
  });

  const allocationComparisonQuery = useQuery({
    queryKey: ["allocation", "comparison"],
    queryFn: () => apiClient.getAllocationComparison(),
  });

  const returnsDailySeriesQuery = useQuery({
    queryKey: ["returns", "daily"],
    queryFn: () => apiClient.getReturnsDailySeries(),
  });

  const incomeSummaryQuery = useQuery({
    queryKey: ["income", "summary"],
    queryFn: () => apiClient.getIncomeSummary(),
  });

  const assetsQuery = useQuery({
    queryKey: ["assets"],
    queryFn: () => apiClient.getAssets(),
  });

  return {
    netWorth: netWorthQuery.data,
    netWorthHistory: netWorthHistoryQuery.data || [],
    allocation: allocationQuery.data || [],
    allocationComparison: allocationComparisonQuery.data || [],
    returnsDailySeries: returnsDailySeriesQuery.data || [],
    incomeSummary: incomeSummaryQuery.data,
    assetsCount: assetsQuery.data?.length || 0,
    isLoading: 
      netWorthQuery.isLoading || 
      netWorthHistoryQuery.isLoading || 
      allocationQuery.isLoading || 
      returnsDailySeriesQuery.isLoading ||
      incomeSummaryQuery.isLoading ||
      assetsQuery.isLoading,
  };
};
