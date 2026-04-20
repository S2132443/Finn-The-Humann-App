import React from "react";
import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  TrendingUp, 
  BarChart3, 
  History, 
  MoreHorizontal 
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Wallet, DollarSign, Settings } from "lucide-react";

const mainNavItems = [
  { icon: LayoutDashboard, label: "Home", path: "/" },
  { icon: TrendingUp, label: "Assets", path: "/assets" },
  { icon: BarChart3, label: "Market", path: "/market" },
  { icon: History, label: "History", path: "/transactions" },
];

const moreNavItems = [
  { icon: Wallet, label: "Accounts", path: "/accounts" },
  { icon: DollarSign, label: "Income", path: "/income" },
  { icon: Settings, label: "Settings", path: "/settings" },
];

export const MobileNav: React.FC = () => {
  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 border-t bg-card/80 backdrop-blur-lg z-50 pb-[env(safe-area-inset-bottom)]">
      <nav className="flex items-center justify-around h-16 px-2">
        {mainNavItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex flex-col items-center justify-center gap-1 flex-1 h-full transition-colors",
              isActive ? "text-emerald-500" : "text-muted-foreground"
            )}
          >
            <item.icon size={20} />
            <span className="text-[10px] font-medium">{item.label}</span>
          </NavLink>
        ))}
        
        <Sheet>
          <SheetTrigger className="flex flex-col items-center justify-center gap-1 flex-1 h-full text-muted-foreground">
            <MoreHorizontal size={20} />
            <span className="text-[10px] font-medium">More</span>
          </SheetTrigger>
          <SheetContent side="bottom" className="rounded-t-3xl h-[40vh]">
            <SheetHeader>
              <SheetTitle>Menu</SheetTitle>
            </SheetHeader>
            <div className="grid grid-cols-3 gap-4 mt-8">
              {moreNavItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-accent/50"
                >
                  <item.icon size={24} className="text-emerald-500" />
                  <span className="text-xs font-medium">{item.label}</span>
                </NavLink>
              ))}
            </div>
          </SheetContent>
        </Sheet>
      </nav>
    </div>
  );
};
