/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    perms: ['admin','editor']    control the page perms (you can set multiple perms)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all perms can be accessed
 */

import { createMemoryHistory, createRouter, createWebHistory, createWebHashHistory, 
  createRouterMatcher} from 'vue-router'
import allbooksfile from '../views/allbook/allbooks.vue'
import csdnpg from '../views/csdn/csdnpg.vue'
import postarticle from '../views/csdn/post.vue'
import zhihupg from '../views/zhihu/zhihupg.vue'
import Home from '../views/home/mainpage.vue'
import markdown_detail from '../views/markdown_detail/detail.vue'
import think from '../views/think/thought.vue'
import think_detail from '../views/think_detail/tkdetail.vue'
import video from '../views/video/index.vue'
import travel from '../views/travel/travel_.vue'
import commonuse from '../views/commonuse/commonuse_.vue'
import everydayimg from '../views/everydayimg/everydayimg_.vue'
import Cookies from 'js-cookie';
import getusername from '/src/common.js'

export const constantRoutes = [
  {
      path: '/book/:id',
      component: allbooksfile,
      name: 'book'
  },
  {
      path: '/zhihu/:id',
      component: zhihupg,
      name: 'zhihu'
  },
  {
      path: '/csdn/:id',
      component: csdnpg,
      name: 'csdn'
  },
  {
    path: '/csdn/post_article/:id',
    component: postarticle,
    name: 'post_article'
  },
  {
    path: '/csdn/markdown_detail/:id',
    component: markdown_detail,
    name: 'markdown_detail',
  },
  {
    path: '/think/:id',
    component: think,
    name: 'think'
  },
  {
    path: '/video/:id',
    component: video,
    name: 'video'
  },
  {
    path: '/travel/:id',
    component: travel,
    name: 'travel'
  },
  {
    path: '/think/detail/:id',
    component: think_detail,
    name: 'think_detail'
  },
  {
    path: '/commonuse/:id',
    component: commonuse,
    name: 'commonuse'
  },
  {
    path: '/everydayimg/:id',
    component: everydayimg,
    name: 'everydayimg'
  },
  {
      path: '/:id',
      component: Home,
      name: 'home',
      // beforeEnter: (to, from, next) => {
      //   const uri = to.query;
      //   const fromuri = from.fullPath;
      //   console.log(to, from, fromuri);
      //   if(fromuri!=null && fromuri!='/zj' && fromuri!='/') {
      //     // next(false);
      //     console.log(to, from, from.fullPath);
      //     router.push(from.fullPath);
      //   } else {
      //     next();
      //   }
      // }
      // beforeEnter: async (to, from, next) => {
      //   const uri = to.query;
      //   const fromuri = from.fullPath;
      //   let gu;
      //   await getusername(document.URL).then((response) => {
      //     gu = response;
      //   });
      //   console.log(to, from, fromuri, gu);
      //   if(fromuri==null || fromuri=='/') {
      //     // next(false);
      //     // console.log(to, from, from.fullPath);
      //     if(gu && gu.ret > 0) {
      //       router.push({ path: '/'+gu.mail});
      //     } else {
      //       router.push({path: "/zj"});
      //     }
      //   } else {
      //     next();
      //   }
      // }
  },
  // {
  //   path: '/',
  //   component: {default:Home},
  //   name: 'home',
  // },
  // {
  //   path: '/pathMatch(.*)',
  //   component: Home,
  //   name: 'home'
  // },
]

const router = createRouter({
  // history: createMemoryHistory(),
  history: createWebHashHistory(),
  // history: createWebHistory(),
  routes:constantRoutes,
})

// router.matcher = createRouterMatcher(router, {end:true})

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
