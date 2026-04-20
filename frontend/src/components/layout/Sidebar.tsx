import React from "react";
import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  Wallet, 
  TrendingUp, 
  BarChart3, 
  History, 
  DollarSign, 
  Settings,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: Wallet, label: "Accounts", path: "/accounts" },
  { icon: TrendingUp, label: "Assets", path: "/assets" },
  { icon: BarChart3, label: "Market", path: "/market" },
  { icon: History, label: "Transactions", path: "/transactions" },
  { icon: DollarSign, label: "Income", path: "/income" },
  { icon: Settings, label: "Settings", path: "/settings" },
];

export const Sidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  return (
    <aside 
      className={cn(
        "hidden md:flex flex-col border-r bg-card transition-all duration-300",
        isCollapsed ? "w-20" : "w-64"
      )}
    >
      <div className="p-6 flex items-center justify-between">
        {!isCollapsed && <h1 className="text-2xl font-bold tracking-tighter text-emerald-500">Finn</h1>}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="ml-auto"
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </Button>
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-3 py-2 rounded-xl transition-colors",
              "hover:bg-accent hover:text-accent-foreground",
              isActive ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground",
              isCollapsed && "justify-center px-0"
            )}
          >
            <item.icon size={20} />
            {!isCollapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="p-6 border-t">
        {!isCollapsed && (
          <div className="text-xs text-muted-foreground">
            © 2024 Finn Investment
          </div>
        )}
      </div>
    </aside>
  );
};
