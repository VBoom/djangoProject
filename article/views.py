from django.shortcuts import render, redirect

# Create your views here.
# 导入 HttpResponse 模块
from django.http import HttpResponse
from django.views import View

from .models import ArticlePost
import markdown
# 引入刚才定义的ArticlePostForm表单类
from .form import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# 引入 Q 对象
from django.db.models import Q
from .models import ArticleColumn

from comment.models import Comment
# 引入评论表单
from comment.forms import CommentForm
from django.shortcuts import get_object_or_404


# 视图函数
def article_list(request):
    # 返回不同排序的对象数组


    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = ArticlePost.objects.all()

    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        # 将 search 参数重置为空
        search = ''
    # 栏目查询集
    if column is not None and column.isdigit():
    #if column is not None:

        article_list = article_list.filter(column=column)
    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])
    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    # 每页显示 16 篇文章
    paginator = Paginator(article_list, 16)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    # dsfsadfa = ArticlePostForm()
    # print("输出来看看：", articles)


    # 取出所有栏目
    column_all = ArticleColumn.objects.all()

    context = {'articles': articles, 'order': order, 'search': search, 'column': column, 'tag': tag, "column_all": column_all}
    return render(request, 'article/list.html', context)
    # return HttpResponse("Hello World!")


def article_detail(request, id):
    # article = ArticlePost.objects.get(id=id)
    article = get_object_or_404(ArticlePost, id=id)
    # 浏览量 +1
    comments = Comment.objects.filter(article=id)

    if request.user != article.author:
        article.total_views += 1
        article.save(update_fields=['total_views'])
    md = markdown.Markdown(extensions=[
                                         'markdown.extensions.extra',
                                         # 语法高亮扩展
                                         'markdown.extensions.codehilite',
                                         # 目录扩展
                                         'markdown.extensions.toc',
                                     ])
    article.body = md.convert(article.body)

    # 引入评论表单
    comment_form = CommentForm()

    context = {'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form, }
    return render(request, 'article/detail.html', context)


# 写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)
            # 处理栏目
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 新增代码，保存 tags 的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form, 'columns': columns }
        # 返回模板
        return render(request, 'article/create.html', context)


# 删文章
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:article_list")

@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse("抱歉，你无权删除这篇文章。")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            # 栏目更新
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            #print("数出来看看：", request.FILES.get('avatar'))

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')


            article.tags.set(request.POST.get('tags').split(','), clear=True)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = { 'article': article, 'article_post_form': article_post_form, 'columns':columns , 'tags': ','.join([x for x in article.tags.names()]),}

        # 将响应返回到模板中
        return render(request, 'article/update.html', context)


class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')