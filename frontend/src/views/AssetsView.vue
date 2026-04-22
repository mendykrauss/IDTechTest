<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAssets, getAssetExportCsvUrl, toggleAsset, deleteAsset } from '../api/index.js'
import AssetTable from '../components/AssetTable.vue'

const route = useRoute()
const router = useRouter()

const ASSET_TYPE_OPTIONS = ['workstation', 'server', 'network', 'peripheral']
const STATUS_OPTIONS = ['active', 'inactive', 'retired']

const normalizeQueryValue = (value) => (typeof value === 'string' ? value : '')
const normalizePage = (value) => {
  const page = Number.parseInt(value, 10)
  return Number.isFinite(page) && page > 0 ? page : 1
}
const normalizeFilter = (value, allowedValues) =>
  allowedValues.includes(value) ? value : ''

const assets = ref([])
const total = ref(0)
const currentPage = ref(normalizePage(route.query.page))
const totalPages = ref(1)
const search = ref(normalizeQueryValue(route.query.search))
const assetType = ref(normalizeFilter(normalizeQueryValue(route.query.type), ASSET_TYPE_OPTIONS))
const status = ref(normalizeFilter(normalizeQueryValue(route.query.status), STATUS_OPTIONS))
const loading = ref(false)
const error = ref(null)

const formatDate = (dateStr) => (dateStr ? dateStr.split('T')[0] : '—')

const syncQueryString = () => {
  const query = {}

  const trimmedSearch = search.value.trim()
  if (trimmedSearch) query.search = trimmedSearch
  if (assetType.value) query.type = assetType.value
  if (status.value) query.status = status.value
  if (currentPage.value > 1) query.page = String(currentPage.value)

  router.replace({ query })
}

const fetchAssets = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await getAssets({
      search: search.value,
      type: assetType.value,
      status: status.value,
      page: currentPage.value,
    })
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

const handleExportCsv = () => {
  const url = getAssetExportCsvUrl({
    search: search.value,
    type: assetType.value,
    status: status.value,
  })

  const link = document.createElement('a')
  link.href = url
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const goToPage = (page) => {
  const nextPage = Math.min(Math.max(page, 1), totalPages.value)
  if (nextPage === currentPage.value) return
  currentPage.value = nextPage
  syncQueryString()
  fetchAssets()
}

watch(search, () => {
  currentPage.value = 1
  syncQueryString()
  fetchAssets()
})

watch(assetType, () => {
  currentPage.value = 1
  syncQueryString()
  fetchAssets()
})

watch(status, () => {
  currentPage.value = 1
  syncQueryString()
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
      <button type="button" class="btn btn-outline-secondary ms-auto me-2" @click="handleExportCsv">
        <i class="bi bi-download me-1"></i>Export CSV
      </button>
      <router-link to="/assets/new" class="btn btn-primary">
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
          <div class="col-12 col-md-3">
            <select v-model="assetType" class="form-select">
              <option value="">All asset types</option>
              <option v-for="type in ASSET_TYPE_OPTIONS" :key="type" :value="type">
                {{ type.charAt(0).toUpperCase() + type.slice(1) }}
              </option>
            </select>
          </div>
          <div class="col-12 col-md-3">
            <select v-model="status" class="form-select">
              <option value="">All statuses</option>
              <option v-for="statusOption in STATUS_OPTIONS" :key="statusOption" :value="statusOption">
                {{ statusOption.charAt(0).toUpperCase() + statusOption.slice(1) }}
              </option>
            </select>
          </div>
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
          <button
            class="page-link"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
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
          <button
            class="page-link"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            <i class="bi bi-chevron-right"></i>
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>
