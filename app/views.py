from django.shortcuts import render,HttpResponseRedirect
from .forms import StudentRegistration,BookingRegistration
from .models import User,Bookings,Bill
from django.http import JsonResponse,HttpResponse
from django.core.paginator import Paginator
from .filters import OrderFilter
from django.views.generic import View
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt

#for generating pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os

def sign_in(request):
    if request.method=='POST':
        fm = AuthenticationForm(request=request,data=request.POST)
        print(fm)
        if fm.is_valid():
            uname = fm.cleaned_data['username']
            upass = fm.cleaned_data['password']
            user = authenticate(username=uname,password=upass)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect('/')
    else:
        fm = AuthenticationForm()
    return render(request,'app/signin.html',{'form':fm})

def log_out(request):
    logout(request)
    return HttpResponseRedirect('/signin/')

@login_required
def index(request):
    data = Bookings.objects.all()
    form = BookingRegistration()
    return render(request,"app/index.html",{'form':form,'data':data})

@login_required
def home(request,id):
    form = StudentRegistration()
    data = User.objects.filter(booking__id=id).order_by('-id')
    myfilter = OrderFilter(request.GET,queryset=data)
    # print(filtered_data)
    book = Bookings.objects.get(pk=id)
    paginator = Paginator(data,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # print(myfilter)
    context = {'form':form,'data':page_obj,'page_obj':page_obj,'ids':id,'book':book,'myfilter':myfilter}
    if request.method=="POST":
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        docket_no = request.POST.get('docketno')
        if( (fromdate and todate) and request.POST.get("download")):
            data_for_pdf = User.objects.filter(date__gte=fromdate,date__lte=todate,booking__id=id).order_by('id')
            total_count = data_for_pdf.count()
            total_pages = total_count//25 + (total_count%25 and True)
            # print('########################33',total_pages)
            final_dict = {}
            temp_c = 0
            i = 1
            temp_dict = []
            total_price = 0
            summary_data = []
            str_for_date = ""
            str_for_cnote = ""
            summary_dict = {}
            grand_total = 0
            prev_str_for_date = ""
            prev_str_for_cnote = ""
            for item in data_for_pdf:
                if(i%24==1):
                    str_for_date += str(item.date)
                    str_for_cnote += str(item.docket_no)
                    prev_str_for_date = str(item.date)
                    prev_str_for_cnote = str(item.docket_no)
                if(i%24==0):
                    str_for_date += " To " + str(item.date)
                    str_for_cnote += " To " + str(item.docket_no)
                    summary_data.append(str_for_date)
                    summary_data.append(str_for_cnote)
                if(i%25 == 0):
                    final_dict[temp_c] = {'filedata' :temp_dict,'price_t':total_price}
                    grand_total += total_price
                    summary_data.append(total_price)
                    summary_dict[temp_c] = summary_data
                    prev_str_for_date = str(item.date)
                    prev_str_for_cnote = str(item.docket_no)
                    str_for_date = ""
                    str_for_cnote = ""
                    summary_data = []
                    temp_dict = []
                    temp_c += 1
                    total_price = 0
                temp_dict.append(item)
                # print(i,temp_c,temp_dict)
                total_price += item.price
                i += 1
            if total_count%25:
                grand_total += total_price
                final_dict[temp_c] = {'filedata' :temp_dict,'price_t':total_price}
            if total_count%24:
                str_for_date = prev_str_for_date + " To " + str(item.date)
                str_for_cnote = prev_str_for_cnote + " To " + str(item.docket_no)
                summary_data.append(str_for_date)
                summary_data.append(str_for_cnote)
                summary_data.append(total_price)
                summary_dict[temp_c] = summary_data
            # print(final_dict)        
            # print(summary_dict)
            summary_row = 16 - len(summary_dict)
            total = grand_total
            gst = 0.18*grand_total
            cgst = gst/2
            sgst = cgst
            final_grand_total = round(gst + total)

            book_data_for_pdf = Bookings.objects.get(pk=id)
            data = {
                'name': book_data_for_pdf.name,
                'all_booking' : final_dict,
                'date':datetime.now,
                'total_page':total_pages,
                'remaining':total_count%24 + 1,
                'summary_dict':summary_dict,
                'summary_rows': summary_row,
                'grand_total':final_grand_total,
                'total':total,
                'cgst':cgst,
                'sgst':sgst,
            }
            # print(type(final_dict))
            pdf = render_to_pdf('app/mcs_pdf.html', data)
            return HttpResponse(pdf, content_type='application/pdf')
        if(fromdate and todate):
            print(fromdate,todate)
            seaarchresult = User.objects.filter(date__gte=fromdate,date__lte=todate,booking__id=id).order_by('-id')
            context['searchresult'] = seaarchresult
            context['searchtrue'] = True
            return render(request,'app/home.html',context = context)
        elif docket_no != '':
            seaarchresult = User.objects.filter(docket_no=docket_no,booking__id=id).order_by('-id')
            context['searchresult'] = seaarchresult
            context['searchtrue'] = True
            return render(request,'app/home.html',context = context)
        else:
            print("date is not present")
            context['date_error'] = True
            return render(request,'app/home.html',context = context)
    return render(request,'app/home.html',context = context)

@login_required
def download_old(request,id,billno):
    print(id,billno)
    book = Bookings.objects.get(pk=id)
    bill = Bill.objects.get(bill_no=billno)
    fromdate = bill.bill_date_from
    todate = bill.bill_date_to
    data_for_pdf = User.objects.filter(date__gte=fromdate,date__lte=todate,booking__id=id).order_by('id')
    total_count = data_for_pdf.count()
    total_pages = total_count//25 + (total_count%25 and True)
    # print('########################33',total_pages)
    final_dict = {}
    temp_c = 0
    i = 1
    temp_dict = []
    total_price = 0
    summary_data = []
    str_for_date = ""
    str_for_cnote = ""
    summary_dict = {}
    grand_total = 0
    prev_str_for_date = ""
    prev_str_for_cnote = ""
    for item in data_for_pdf:
        if(i%24==1):
            str_for_date += str(item.date)
            str_for_cnote += str(item.docket_no)
            prev_str_for_date = str(item.date)
            prev_str_for_cnote = str(item.docket_no)
        if(i%24==0):
            str_for_date += " To " + str(item.date)
            str_for_cnote += " To " + str(item.docket_no)
            summary_data.append(str_for_date)
            summary_data.append(str_for_cnote)
        if(i%25 == 0):
            final_dict[temp_c] = {'filedata' :temp_dict,'price_t':total_price}
            grand_total += total_price
            summary_data.append(total_price)
            summary_dict[temp_c] = summary_data
            prev_str_for_date = str(item.date)
            prev_str_for_cnote = str(item.docket_no)
            str_for_date = ""
            str_for_cnote = ""
            summary_data = []
            temp_dict = []
            temp_c += 1
            total_price = 0
        temp_dict.append(item)
        # print(i,temp_c,temp_dict)
        total_price += item.price
        i += 1
    if total_count%25:
        grand_total += total_price
        final_dict[temp_c] = {'filedata' :temp_dict,'price_t':total_price}
    if total_count%24:
        str_for_date = prev_str_for_date + " To " + str(item.date)
        str_for_cnote = prev_str_for_cnote + " To " + str(item.docket_no)
        summary_data.append(str_for_date)
        summary_data.append(str_for_cnote)
        summary_data.append(total_price)
        summary_dict[temp_c] = summary_data
    # print(final_dict)        
    # print(summary_dict)
    summary_row = 16 - len(summary_dict)
    total = grand_total
    gst = 0.18*grand_total
    cgst = gst/2
    sgst = cgst
    final_grand_total = round(gst + total)

    book_data_for_pdf = Bookings.objects.get(pk=id)
    data = {
        'name': book_data_for_pdf.name,
        'all_booking' : final_dict,
        'date':datetime.now,
        'total_page':total_pages,
        'remaining':total_count%24 + 1,
        'summary_dict':summary_dict,
        'summary_rows': summary_row,
        'grand_total':final_grand_total,
        'total':total,
        'cgst':cgst,
        'sgst':sgst,
        'billno':billno,
    }
    # print(type(final_dict))
    pdf = render_to_pdf('app/mcs_pdf.html', data)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "%s_%s.pdf" %(book.name,billno)
        content = "inline; filename='%s'" %(filename)
        #download = request.GET.get("download")
        #if download:
        content = "attachment; filename=%s" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")
    # return HttpResponse(pdf, content_type='application/pdf')

@login_required
def generatebill(request,id):
    book = Bookings.objects.get(pk=id)
    try:
        last_bill_no = Bill.objects.filter(billof__id=id).last()
    except:
        last_bill_no = 0
    old_bills = Bill.objects.filter(billof__id=id).order_by('-id')
    paginator = Paginator(old_bills,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = { 
        'ids':id,
        'old_bills':old_bills,
        'book':book,
        'last_bill_no':last_bill_no,
        'page_obj':page_obj,
    }
    if request.method=='POST':
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        billno = request.POST.get('billno')
        print(fromdate,todate,billno)
        if((not billno) or (not fromdate) or (not todate)):
            context['error'] = True
            return render(request,'app/generatebill.html',context = context)
        if( (fromdate and todate) and request.POST.get("download")):
            data_for_pdf = User.objects.filter(date__gte=fromdate,date__lte=todate,booking__id=id).order_by('id')
            total_count = data_for_pdf.count()
            total_pages = total_count//25 + (total_count%25 and True)
            # print('########################33',total_pages)
            final_dict = {}
            temp_c = 0
            i = 1
            temp_dict = []
            total_price = 0
            summary_data = []
            str_for_date = ""
            str_for_cnote = ""
            summary_dict = {}
            grand_total = 0
            prev_str_for_date = ""
            prev_str_for_cnote = ""
            for item in data_for_pdf:
                if(i%24==1):
                    str_for_date += str(item.date)
                    str_for_cnote += str(item.docket_no)
                    prev_str_for_date = str(item.date)
                    prev_str_for_cnote = str(item.docket_no)
                if(i%24==0):
                    str_for_date += " To " + str(item.date)
                    str_for_cnote += " To " + str(item.docket_no)
                    summary_data.append(str_for_date)
                    summary_data.append(str_for_cnote)
                if(i%25 == 0):
                    final_dict[temp_c] = {'filedata' :temp_dict,'price_t':total_price}
                    grand_total += total_price
                    summary_data.append(total_price)
                    summary_dict[temp_c] = summary_data
                    prev_str_for_date = str(item.date)
                    prev_str_for_cnote = str(item.docket_no)
                    str_for_date = ""
                    str_for_cnote = ""
                    summary_data = []
                    temp_dict = []
                    temp_c += 1
                    total_price = 0
                temp_dict.append(item)
                # print(i,temp_c,temp_dict)
                total_price += item.price
                i += 1
            if total_count%25:
                grand_total += total_price
                final_dict[temp_c] = {'filedata' :temp_dict,'price_t':total_price}
            if total_count%24:
                str_for_date = prev_str_for_date + " To " + str(item.date)
                str_for_cnote = prev_str_for_cnote + " To " + str(item.docket_no)
                summary_data.append(str_for_date)
                summary_data.append(str_for_cnote)
                summary_data.append(total_price)
                summary_dict[temp_c] = summary_data
            # print(final_dict)        
            # print(summary_dict)
            summary_row = 16 - len(summary_dict)
            total = grand_total
            gst = 0.18*grand_total
            cgst = gst/2
            sgst = cgst
            final_grand_total = round(gst + total)

            book_data_for_pdf = Bookings.objects.get(pk=id)
            data = {
                'name': book_data_for_pdf.name,
                'all_booking' : final_dict,
                'date':datetime.now,
                'total_page':total_pages,
                'remaining':total_count%24 + 1,
                'summary_dict':summary_dict,
                'summary_rows': summary_row,
                'grand_total':final_grand_total,
                'total':total,
                'cgst':cgst,
                'sgst':sgst,
                'billno':billno,
            }
            # print(type(final_dict))
            pdf = render_to_pdf('app/mcs_pdf.html', data)
            if pdf:
                billusr = Bill(billof=book,bill_no=billno,bill_date_from=fromdate,bill_date_to=todate,price=final_grand_total)
                billusr.save()
            return HttpResponse(pdf, content_type='application/pdf')
    return render(request,'app/generatebill.html',context = context)

@login_required
def save_data_book(request):
    if request.method == "POST":
        form = BookingRegistration(request.POST)
        if form.is_valid():
            sid = request.POST.get('stuid')
            name = request.POST['name']
            email = request.POST['email']
            if(sid == ''):
                usr = Bookings(name=name,email=email)
            else:
                usr = Bookings(id = sid,name=name,email=email)
            usr.save()
            data = Bookings.objects.values()
            mydata = list(data)
            # print(mydata)
            return JsonResponse({'status':'Save','mydata':mydata})
        else:
            return JsonResponse({'status':0})

@login_required
def edit_data_book(request):
    if request.method == "POST":
        id = request.POST.get('sid')
        data = Bookings.objects.get(pk=id)
        # print('################',data.name)
        mydata = {"id":data.id,"name":data.name,"email":data.email}
        return JsonResponse(mydata)

# @csrf_exempt
@login_required
def save_data(request,id):
    if request.method == "POST":
        form = StudentRegistration(request.POST)
        if form.is_valid():
            sid = request.POST.get('stuid')
            name = request.POST['name']
            city = request.POST['city']
            weight = request.POST['weight']
            docket_no = request.POST['docket_no']
            date = request.POST['date']
            price = request.POST['price']          
            sn = Bookings.objects.get(id=id)
            sno = sn.s_no
            if(sid == ''):
                sno = sno + 1
                sn.s_no = sno
                sn.save()
                usr = User(name=name,city=city,weight=weight,docket_no=docket_no,date=date,price=price,booking_id=id,sno=sno)
            else:
                usr = User(id = sid,name=name,city=city,weight=weight,docket_no=docket_no,date=date,price=price,booking_id=id,sno=sno)
            usr.save()
            data = User.objects.values().filter(booking__id=id).order_by('-id')[:5]                                                                                                                                                                                                         
            # print(data)
            mydata = list(data)
            return JsonResponse({'status':'Save','mydata':mydata,'ids':id})
        else:
            return JsonResponse({'status':0})

@login_required
def edit_data(request,id):
    if request.method == "POST":
        id = request.POST.get('sid')
        print(id)
        data = User.objects.get(pk=id)
        mydata = {"id":data.id,"name":data.name,"city":data.city,"weight":data.weight,'price':data.price,'date':data.date,'docket_no':data.docket_no}
        return JsonResponse(mydata)


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class Generatepdf(View):
    def get(self, request, id, *args, **kwargs):
        if request.method=="POST":
            fromdate = request.POST.get('fromdate')
            todate = request.POST.get('todate')
            print(fromdate,todate)
        # try:
        data_for_pdf = User.objects.filter(booking__id=id).order_by('-id')
        book_data_for_pdf = Bookings.objects.get(pk=id)
        # except:
        #     return HttpResponse("505 Not Found")
        print(data_for_pdf,book_data_for_pdf)
        data = {
            'name': book_data_for_pdf.name,
            'all_booking' : data_for_pdf
        }
        pdf = render_to_pdf('app/pdf_html.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

        # force download
        # if pdf:
        #     response = HttpResponse(pdf, content_type='application/pdf')
        #     filename = "Invoice_%s.pdf" %(data['order_id'])
        #     content = "inline; filename='%s'" %(filename)
        #     #download = request.GET.get("download")
        #     #if download:
        #     content = "attachment; filename=%s" %(filename)
        #     response['Content-Disposition'] = content
        #     return response
        # return HttpResponse("Not found")