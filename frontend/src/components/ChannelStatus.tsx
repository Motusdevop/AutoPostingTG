import { cn } from "@/lib/utils";

interface ChannelStatusProps {
  active: boolean;
  hasError?: boolean;
}

export const ChannelStatus = ({ active, hasError }: ChannelStatusProps) => {
  const getStatusColor = () => {
    if (hasError) return "bg-red-500";
    if (active) return "bg-green-500";
    return "bg-yellow-500";
  };

  return (
    <div className="flex items-center gap-2">
      <div
        className={cn(
          "h-3 w-3 rounded-full",
          getStatusColor()
        )}
      />
      <span className="text-sm text-gray-600">
        {hasError ? "Ошибка" : active ? "Активен" : "Неактивен"}
      </span>
    </div>
  );
};