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
    <div class="tag-filter">
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
      <input
        v-model="keyword"
        type="text"
        placeholder="게시글 검색어를 입력하세요"
        @keyup.enter="search"
      />
      <button class="btn btn-ghost" @click="search">검색</button>
      <button class="btn btn-primary" @click="goWrite">+ 글쓰기</button>
    </div>

    <div v-if="loading" class="empty">불러오는 중…</div>
    <div v-else-if="posts.length === 0" class="empty">
      아직 이 구에 등록된 이야기가 없어요. 첫 글의 주인공이 되어보세요 🌱
    </div>

    <table v-else class="post-table">
      <thead>
        <tr>
          <th class="col-tag">말머리</th>
          <th>제목</th>
          <th>닉네임</th>
          <th>조회</th>
          <th>작성일</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in posts" :key="p.board_id" @click="goDetail(p.board_id)">
          <td class="col-tag">
           <span class="tag-badge">{{ p.category }}</span>
          </td>
          <td class="title-cell">{{ p.title }}</td>
          <td>{{ p.writer }}</td>
          <td>{{ p.view_count }}</td>
          <td>{{ formatDate(p.created_at) }}</td>
        </tr>
      </tbody>
    </table>

    <div class="pager">
      <button class="btn btn-ghost" :disabled="page === 1" @click="page--">
        이전
      </button>
      <span>{{ page }} 페이지</span>
      <button class="btn btn-ghost" :disabled="!hasMore" @click="page++">
        다음
      </button>
    </div>
  </div>
</template>

<style scoped>
.post-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tag-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-chip {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  font-size: var(--text-xs);
  color: var(--forest-700);
}

.tag-chip.active {
  background: var(--forest-600);
  color: white;
  border-color: var(--forest-600);
}

.toolbar {
  display: flex;
  gap: 8px;
}

.toolbar input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
}

.empty {
  padding: 48px 0;
  text-align: center;
  color: var(--moss-400);
}

.post-table {
  width: 100%;
  border-collapse: collapse;
}

.post-table th {
  text-align: left;
  font-size: var(--text-xs);
  color: var(--moss-400);
  border-bottom: 1px solid var(--line);
  padding: 8px 4px;
}

.col-tag {
  width: 84px;
}

.post-table td {
  padding: 12px 4px;
  border-bottom: 1px solid var(--line);
  font-size: var(--text-sm);
}

.post-table tr {
  cursor: pointer;
}

.post-table tr:hover td {
  background: var(--surface-alt);
}

.tag-badge {
  font-size: var(--text-xs);
  background: var(--surface-alt);
  color: var(--forest-700);
  padding: 3px 8px;
  border-radius: 999px;
}

.title-cell {
  font-weight: 600;
  color: var(--forest-900);
}

.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: var(--text-sm);
}
</style>
