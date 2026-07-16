<script setup>
import { ref, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import client from "../api/client";
import { POST_CATEGORIES } from "../composables/districts";

const props = defineProps({
  gu: { type: String, required: true },
});

const router = useRouter();
const posts = ref([]);
const keyword = ref("");
const category = ref(""); // "" = 전체
const page = ref(1);
const size = 10;
const loading = ref(false);
const hasMore = ref(true);

async function fetchPosts() {
  loading.value = true;
  try {
    const { data } = await client.get("/api/boards", {
      params: {
        gu: props.gu,
        keyword: keyword.value || undefined,
        page: page.value,
        size,
      },
    });
    posts.value = data;
    hasMore.value = data.length === size;
  } finally {
    loading.value = false;
  }
}

function search() {
  page.value = 1;
  fetchPosts();
}

function selectCategory(cat) {
  category.value = category.value === cat ? "" : cat;
  page.value = 1;
  fetchPosts();
}

function goDetail(id) {
  router.push({ name: "post-detail", params: { gu: props.gu, id } });
}

function goWrite() {
  router.push({ name: "post-new", params: { gu: props.gu } });
}

function formatDate(iso) {
  return iso?.slice(0, 10) ?? "";
}

watch(page, fetchPosts);
onMounted(fetchPosts);
</script>

<template>
  <div class="post-list">
    <div v-if="POST_CATEGORIES && POST_CATEGORIES.length > 0" class="tag-filter">
      <button
        v-for="cat in POST_CATEGORIES"
        :key="cat"
        class="tag-chip"
        :class="{ active: category === cat }"
        @click="selectCategory(cat)"
      >
        {{ cat }}
      </button>
    </div>

    <div class="toolbar">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input
          v-model="keyword"
          type="text"
          placeholder="동네의 어떤 이야기가 궁금하신가요?"
          @keyup.enter="search"
        />
      </div>
      <button class="btn btn-ghost search-btn" @click="search">검색</button>
      <button class="btn btn-primary" @click="goWrite">+ 새 글 쓰기</button>
    </div>

    <div v-if="loading" class="empty">
      <div class="spinner"></div>
      <p>숲에서 속삭임을 찾아내는 중…</p>
    </div>
    
    <div v-else-if="posts.length === 0" class="empty">
      <span class="empty-icon">🌱</span>
      <p>아직 이 구에 등록된 이야기가 없어요.<br />동네의 따뜻한 소식을 먼저 들려주세요!</p>
    </div>

    <div v-else class="table-container card">
      <table class="post-table">
        <thead>
          <tr>
            <th class="col-tag">말머리</th>
            <th class="col-title">제목</th>
            <th class="col-writer">작성자</th>
            <th class="col-view">조회수</th>
            <th class="col-date">작성일</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in posts" :key="p.board_id" @click="goDetail(p.board_id)">
            <td class="col-tag">
              <span class="tag-badge">{{ p.category || "잡담" }}</span>
            </td>
            <td class="title-cell">
              <div class="title-wrapper">
                <span class="title-text">{{ p.title }}</span>
              </div>
            </td>
            <td class="writer-cell">{{ p.writer }}</td>
            <td class="view-cell">{{ p.view_count }}</td>
            <td class="date-cell">{{ formatDate(p.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pager">
      <button class="btn btn-ghost pager-btn" :disabled="page === 1" @click="page--">
        이전
      </button>
      <span class="page-num">{{ page }} 페이지</span>
      <button class="btn btn-ghost pager-btn" :disabled="!hasMore" @click="page++">
        다음
      </button>
    </div>
  </div>
</template>

<style scoped>
.post-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tag-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  font-size: var(--text-sm);
  color: var(--forest-700);
  font-weight: 700;
  transition: all 0.2s var(--ease-leaf);
}

.tag-chip:hover {
  border-color: var(--forest-600);
  background: var(--surface-alt);
}

.tag-chip.active {
  background: var(--forest-600);
  color: white;
  border-color: var(--forest-600);
  box-shadow: 0 4px 12px rgba(37, 68, 42, 0.12);
}

.toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--moss-400);
  font-size: 14px;
}

.toolbar input {
  width: 100%;
  padding: 12px 14px 12px 38px;
  border: 1.5px solid var(--line);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  box-shadow: inset 0 1px 2px rgba(18, 33, 22, 0.01);
  transition: all 0.2s var(--ease-leaf);
}

.toolbar input:focus {
  border-color: var(--moss-400);
  box-shadow: 0 0 0 3px rgba(85, 123, 107, 0.12);
}

.search-btn {
  padding: 12px 20px;
}

.empty {
  padding: 64px 0;
  text-align: center;
  color: var(--moss-400);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  font-size: 36px;
}

.empty p {
  font-size: var(--text-sm);
  line-height: 1.6;
  font-weight: 500;
  margin: 0;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--line);
  border-top-color: var(--forest-600);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 🌿 리스트 테이블 카드 디자인화 */
.table-container {
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  background: var(--surface);
  box-shadow: var(--shadow-soft);
}

.post-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.post-table th {
  font-size: var(--text-xs);
  color: var(--moss-400);
  font-weight: 700;
  border-bottom: 1.5px solid var(--line);
  padding: 14px 16px;
  background: rgba(244, 247, 242, 0.4);
}

.post-table td {
  padding: 16px 16px;
  border-bottom: 1px solid var(--line);
  font-size: var(--text-sm);
  color: var(--forest-700);
}

.post-table tr {
  cursor: pointer;
  transition: background-color 0.18s var(--ease-leaf);
}

.post-table tr:hover td {
  background: rgba(233, 240, 230, 0.45);
}

.post-table tr:last-child td {
  border-bottom: none;
}

/* 열 넓이 가로 균형 매핑 */
.col-tag { width: 100px; text-align: center; }
.col-title { width: auto; }
.col-writer { width: 120px; }
.col-view { width: 80px; text-align: center; }
.col-date { width: 110px; text-align: right; }

.post-table td.col-tag {
  text-align: center;
}

.tag-badge {
  font-size: var(--text-xs);
  font-weight: 700;
  background: var(--surface-alt);
  color: var(--forest-700);
  padding: 4px 10px;
  border-radius: 999px;
  display: inline-block;
}

.title-cell {
  font-weight: 700;
  color: var(--forest-900);
}

.title-text {
  transition: color 0.15s var(--ease-leaf);
}

.post-table tr:hover .title-text {
  color: var(--forest-600);
}

.writer-cell {
  font-weight: 500;
  color: var(--forest-700);
}

.view-cell {
  text-align: center;
  color: var(--moss-400);
}

.date-cell {
  text-align: right;
  color: var(--moss-400);
  font-variant-numeric: tabular-nums;
}

/* 페이징 */
.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
}

.pager-btn {
  padding: 8px 18px;
  font-size: var(--text-sm);
  border-radius: var(--radius-sm);
}

.page-num {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--forest-900);
}
</style>