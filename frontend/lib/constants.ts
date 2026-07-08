export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const EXAMPLE_TOPICS = [
  "Brain Tumor Segmentation using Deep Learning",
  "Retrieval-Augmented Generation for Question Answering",
  "Federated Learning for Healthcare",
  "Lightweight Transformers for Edge Devices",
];

export const PIPELINE_STAGES = [
  { key: "search", label: "Collecting papers" },
  { key: "analyze", label: "Extracting structured data" },
  { key: "gaps", label: "Detecting research gaps" },
  { key: "directions", label: "Generating project ideas" },
] as const;

export type PipelineStageKey = (typeof PIPELINE_STAGES)[number]["key"];
