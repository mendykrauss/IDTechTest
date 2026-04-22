<script setup>
import { ref, onMounted, watch } from 'vue'
import { getAssets, toggleAsset, deleteAsset } from '../api/index.js'
import AssetTable from '../components/AssetTable.vue'

const assets = ref([])
const total = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)
const search = ref('')
const loading = ref(false)
const error = ref(null)

const formatDate = (dateStr) => (dateStr ? dateStr.split('T')[0] : '—')

const fetchAssets = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await getAssets({ search: search.value, page: currentPage.value })
    assets.value = data.assets.map((a) => ({
      ...a,
      last_seen_formatted: formatDate(a.last_seen),
    }))
    total.value = data.total
    totalPages.value = data.pages
  } catch (err) {
    error.value = 'Failed to load assets. Is the backend running?'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleToggle = async (asset) => {
  await toggleAsset(asset.id)
  fetchAssets()
}

const handleDelete = async (asset) => {
  if (!confirm(`Delete "${asset.name}"? This cannot be undone.`)) return
  await deleteAsset(asset.id)
  fetchAssets()
}

const goToPage = (page) => {
  currentPage.value = page
  fetchAssets()
}

watch(search, () => {
  currentPage.value = 1
  fetchAssets()
})

onMounted(fetchAssets)
</script>

<template>
  <div>
    <div class="d-flex align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Assets</h1>
        <p class="text-muted mb-0">{{ total }} total asset{{ total !== 1 ? 's' : '' }}</p>
      </div>
      <router-link to="/assets/new" class="btn btn-primary ms-auto">
        <i class="bi bi-plus-lg me-1"></i>Add Asset
      </router-link>
    </div>

    <!-- Search -->
    <div class="card mb-3">
      <div class="card-body py-2">
        <div class="row g-2 align-items-center">
          <div class="col">
            <div class="input-group">
              <span class="input-group-text bg-transparent border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input
                v-model="search"
                type="text"
                class="form-control border-start-0 ps-0"
                placeholder="Search assets…"
              />
            </div>
          </div>
          <!--
            Feature 3: Add "Asset Type" and "Status" filter dropdowns here.
            The backend already accepts ?type= and ?status= query params on GET /api/assets.
            Wire them up so selecting a filter re-fetches the list reactively.
          -->
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5 text-muted">
      <div class="spinner-border spinner-border-sm me-2"></div>
      Loading…
    </div>

    <!-- Table -->
    <div v-else class="card">
      <div class="card-body p-0">
        <AssetTable
          :assets="assets"
          @toggle="handleToggle"
          @delete="handleDelete"
        />
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="mt-3" aria-label="Asset pages">
      <ul class="pagination justify-content-center mb-0">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" @click="goToPage(currentPage - 1)">
            <i class="bi bi-chevron-left"></i>
          </button>
        </li>
        <li
          v-for="p in totalPages"
          :key="p"
          class="page-item"
          :class="{ active: p === currentPage }"
        >
          <button class="page-link" @click="goToPage(p)">{{ p }}</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button class="page-link" @click="goToPage(currentPage + 1)">
            <i class="bi bi-chevron-right"></i>
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>
