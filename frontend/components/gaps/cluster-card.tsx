import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EvidenceTrail } from "@/components/gaps/evidence-trail";
import type { ClusterSummary, Paper } from "@/lib/types";

interface ClusterCardProps {
  cluster: ClusterSummary;
  papersById: Map<number, Paper>;
}

export function ClusterCard({ cluster, papersById }: ClusterCardProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{cluster.theme}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {cluster.common_methods.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {cluster.common_methods.map((method) => (
              <Badge key={method} variant="teal">
                {method}
              </Badge>
            ))}
          </div>
        )}
        {cluster.common_datasets.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {cluster.common_datasets.map((dataset) => (
              <Badge key={dataset} variant="default">
                {dataset}
              </Badge>
            ))}
          </div>
        )}
        <EvidenceTrail paperIds={cluster.paper_ids} papersById={papersById} />
      </CardContent>
    </Card>
  );
}
