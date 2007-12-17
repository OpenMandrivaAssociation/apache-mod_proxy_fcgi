#Module-Specific definitions
%define mod_name mod_proxy_fcgi
%define mod_conf 32_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Mod_proxy_fcgi is a DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	0
Release:	%mkrel 3
Group:		System/Servers
License:	Apache License
URL:		http://www.apache.org/
Source0:	mod_proxy_fcgi.c
Source1:	fcgi_protocol.h
Source2:	fcgistarter.c
Source3:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	apache-mod_proxy >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file

%description
Mod_proxy_fcgi is a DSO module for the apache web server.

%prep

%setup -q -c -T -n %{mod_name}-%{version}

cp %{SOURCE0} .
cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%{_sbindir}/apxs -c %{mod_name}.c

gcc \
    -I`%{_sbindir}/apxs -q INCLUDEDIR` \
    `%{_bindir}/apr-1-config --includes` \
    `%{_sbindir}/apxs -q CFLAGS` \
    `%{_bindir}/apr-1-config --cppflags` \
    `%{_bindir}/apr-1-config --link-ld` \
    `%{_bindir}/apr-1-config --libs` \
    -o fcgistarter fcgistarter.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_sbindir}

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0755 fcgistarter %{buildroot}%{_sbindir}
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,root,root) %{_sbindir}/fcgistarter


