"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DentalOdontogram } from "@/components/dental/odontogram";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Calendar, Plus, History, Save } from "lucide-react";
import { formatDate, getToothName } from "@/lib/utils";
import { ToothCondition } from "@/types";

// Mock dental data
const mockDentalRecord = {
  id: "1",
  patient: "patient-123",
  last_cleaning_date: "2024-06-15",
  next_cleaning_date: "2024-12-15",
  notes: "Patient has good oral hygiene. Recommended flossing daily.",
  tooth_history: [
    { id: "1", tooth_number: 3, surface: "occlusal", condition: "filled" as ToothCondition, treatment: "Amalgam filling", treatment_date: "2024-01-15", notes: "" },
    { id: "2", tooth_number: 14, surface: "mesial", condition: "cavity" as ToothCondition, treatment: "Pending treatment", treatment_date: "2024-11-20", notes: "Small cavity detected" },
    { id: "3", tooth_number: 19, surface: "occlusal", condition: "crown" as ToothCondition, treatment: "Porcelain crown", treatment_date: "2023-08-10", notes: "Root canal performed first" },
    { id: "4", tooth_number: 30, surface: "buccal", condition: "root_canal" as ToothCondition, treatment: "Root canal therapy", treatment_date: "2023-05-22", notes: "" },
    { id: "5", tooth_number: 1, surface: "", condition: "missing" as ToothCondition, treatment: "Extracted due to decay", treatment_date: "2022-03-15", notes: "Wisdom tooth" },
    { id: "6", tooth_number: 16, surface: "", condition: "missing" as ToothCondition, treatment: "Extracted due to impaction", treatment_date: "2022-03-15", notes: "Wisdom tooth" },
  ],
};

const toothConditions: ToothCondition[] = [
  "healthy",
  "cavity",
  "filled",
  "crown",
  "root_canal",
  "extraction",
  "missing",
  "implant",
  "bridge",
];

const surfaces = ["occlusal", "mesial", "distal", "buccal", "lingual", "incisal"];

export default function DentalRecordsPage() {
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);
  const [addTreatmentOpen, setAddTreatmentOpen] = useState(false);
  const [treatmentForm, setTreatmentForm] = useState({
    condition: "" as ToothCondition,
    surface: "",
    treatment: "",
    notes: "",
  });

  const handleToothClick = (toothNumber: number) => {
    setSelectedTooth(toothNumber);
  };

  const handleAddTreatment = () => {
    if (!selectedTooth) return;
    // In real app, save to API
    console.log("Adding treatment:", { tooth: selectedTooth, ...treatmentForm });
    setAddTreatmentOpen(false);
    setTreatmentForm({ condition: "" as ToothCondition, surface: "", treatment: "", notes: "" });
  };

  const getToothHistory = (toothNumber: number) => {
    return mockDentalRecord.tooth_history.filter((h) => h.tooth_number === toothNumber);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dental Records</h1>
          <p className="text-muted-foreground">
            Interactive dental chart and treatment history
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <History className="h-4 w-4 mr-2" />
            View History
          </Button>
          <Button>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      {/* Cleaning Schedule */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Last Cleaning</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatDate(mockDentalRecord.last_cleaning_date)}
            </div>
            <p className="text-xs text-muted-foreground">
              Professional cleaning performed
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Next Cleaning Due</CardTitle>
            <Calendar className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {formatDate(mockDentalRecord.next_cleaning_date)}
            </div>
            <p className="text-xs text-muted-foreground">
              Schedule appointment soon
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Odontogram */}
      <Card>
        <CardHeader>
          <CardTitle>Dental Chart (Odontogram)</CardTitle>
          <CardDescription>
            Click on a tooth to view details or record treatment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DentalOdontogram
            teeth={mockDentalRecord.tooth_history}
            onToothClick={handleToothClick}
          />
        </CardContent>
      </Card>

      {/* Selected Tooth Details */}
      {selectedTooth && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Tooth #{selectedTooth}</CardTitle>
              <CardDescription>{getToothName(selectedTooth)}</CardDescription>
            </div>
            <Button onClick={() => setAddTreatmentOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Treatment
            </Button>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="history">
              <TabsList>
                <TabsTrigger value="history">Treatment History</TabsTrigger>
                <TabsTrigger value="notes">Notes</TabsTrigger>
              </TabsList>
              <TabsContent value="history" className="mt-4">
                {getToothHistory(selectedTooth).length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">
                    No treatment history for this tooth
                  </p>
                ) : (
                  <div className="space-y-4">
                    {getToothHistory(selectedTooth).map((history) => (
                      <div
                        key={history.id}
                        className="flex items-start justify-between p-4 bg-muted/50 rounded-lg"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{history.treatment}</span>
                            <Badge variant="secondary" className="capitalize">
                              {history.condition.replace("_", " ")}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {history.surface && `Surface: ${history.surface} · `}
                            {formatDate(history.treatment_date)}
                          </p>
                          {history.notes && (
                            <p className="text-sm">{history.notes}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>
              <TabsContent value="notes" className="mt-4">
                <textarea
                  className="w-full h-32 p-3 border rounded-md"
                  placeholder="Add notes about this tooth..."
                />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Recent Treatments */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Treatments</CardTitle>
          <CardDescription>All dental treatments and procedures</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockDentalRecord.tooth_history
              .sort((a, b) => new Date(b.treatment_date).getTime() - new Date(a.treatment_date).getTime())
              .map((history) => (
                <div
                  key={history.id}
                  className="flex items-center justify-between p-4 bg-muted/50 rounded-lg"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary">
                      {history.tooth_number}
                    </div>
                    <div>
                      <p className="font-medium">{history.treatment}</p>
                      <p className="text-sm text-muted-foreground">
                        {getToothName(history.tooth_number)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="secondary" className="capitalize">
                      {history.condition.replace("_", " ")}
                    </Badge>
                    <p className="text-sm text-muted-foreground mt-1">
                      {formatDate(history.treatment_date)}
                    </p>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Add Treatment Dialog */}
      <Dialog open={addTreatmentOpen} onOpenChange={setAddTreatmentOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Treatment</DialogTitle>
            <DialogDescription>
              Record a new treatment for Tooth #{selectedTooth}
              {selectedTooth && ` (${getToothName(selectedTooth)})`}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Condition</Label>
              <Select
                value={treatmentForm.condition}
                onValueChange={(value) =>
                  setTreatmentForm({ ...treatmentForm, condition: value as ToothCondition })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select condition" />
                </SelectTrigger>
                <SelectContent>
                  {toothConditions.map((condition) => (
                    <SelectItem key={condition} value={condition}>
                      {condition.replace("_", " ")}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Surface (if applicable)</Label>
              <Select
                value={treatmentForm.surface}
                onValueChange={(value) =>
                  setTreatmentForm({ ...treatmentForm, surface: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select surface" />
                </SelectTrigger>
                <SelectContent>
                  {surfaces.map((surface) => (
                    <SelectItem key={surface} value={surface}>
                      {surface}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Treatment Performed</Label>
              <Input
                value={treatmentForm.treatment}
                onChange={(e) =>
                  setTreatmentForm({ ...treatmentForm, treatment: e.target.value })
                }
                placeholder="e.g., Composite filling, Crown preparation"
              />
            </div>
            <div className="space-y-2">
              <Label>Notes</Label>
              <textarea
                className="w-full h-24 p-3 border rounded-md text-sm"
                value={treatmentForm.notes}
                onChange={(e) =>
                  setTreatmentForm({ ...treatmentForm, notes: e.target.value })
                }
                placeholder="Additional notes..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddTreatmentOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddTreatment}>Save Treatment</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
