# 🎨 ChainOpera-Style Redesign Plan

## 📋 Overview
Transform Langflow from project-centric to workflow-centric architecture inspired by ChainOpera.

## ✅ Phase 1: Core Structure (IN PROGRESS)

### 1.1 Store Changes
- [ ] **foldersStore.tsx** → Simplify or deprecate (workflows are flat, not folder-based)
- [ ] **flowsManagerStore.ts** → Update to workflow-first model
- [ ] **utilityStore.ts** → Remove defaultFolderName references
- [ ] **Add workflowStore.ts** → New store for workflow templates

### 1.2 Routing Changes  
- [ ] **routes.tsx**:
  - Change `/flows` → `/workflows` (or keep `/` as main workflows page)
  - Remove folder/project hierarchy from routes
  - Update navigation to: Home (Workflows) / Agent / Settings / Admin

### 1.3 Navigation/Sidebar
- [ ] **Update sidebar** to match ChainOpera:
  ```
  + Create Workflow (green button)
  Home (Workflows icon)
  Agent
  Workflow (current page indicator)
  MCP Servers
  Models APIs
  Knowledge
  Agent Servers
  AgentOpera
  ─────────
  Api Key
  Settings
  ```

## 🎯 Phase 2: UI Components (NEXT)

### 2.1 Main Workflows Page
- [ ] **Create WorkflowTemplatesPage**:
  - Tab: "Workflow Templates" | "My Workflows"
  - Template categories sidebar
  - Colorful workflow cards (like ChainOpera)
  - Grid layout with hover effects

### 2.2 Workflow Cards
- [ ] Colorful gradient backgrounds
- [ ] Modern card design with icons
- [ ] Use Cases: Assistants, Classification, Coding, Content Generation, Q&A, etc.
- [ ] Methodology: Prompting, RAG, Agents

### 2.3 Dialogs & Modals
- [ ] "New Flow" → "Create Workflow"
- [ ] Workflow template picker dialog
- [ ] Modern modal styling

## 🎨 Phase 3: Styling & Polish (LATER)

### 3.1 Dark Theme
- [ ] Ensure consistent dark theme across all pages
- [ ] Update color palette to match modern AI SaaS
- [ ] Add subtle animations

### 3.2 Modern UI Elements
- [ ] Gradient buttons and cards
- [ ] Better spacing and typography
- [ ] Loading states and transitions

---

## 📁 Files to Modify (Phase 1)

### Priority 1: Core Navigation
1. `src/frontend/src/routes.tsx` - Update routing structure
2. `src/frontend/src/pages/MainPage/pages/main-page/index.tsx` - Transform to workflows page
3. `src/frontend/src/stores/foldersStore.tsx` - Simplify/deprecate

### Priority 2: Stores
4. `src/frontend/src/stores/flowsManagerStore.ts` - Workflow-first model
5. `src/frontend/src/stores/utilityStore.ts` - Remove folder references

### Priority 3: Components
6. Sidebar/Navigation components
7. Header components

---

## 🚀 Starting Implementation

**Current Task**: Modifying routing to be workflow-first...
