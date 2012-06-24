%define 	apxs	/usr/sbin/apxs
Summary:	Antihak module for Apache
Summary(pl):	Modu� antihak dla Apache
Name:		apache-mod_antihak
Version:	0.3.1beta
Release:	2
License:	GPL
Group:		Networking/Daemons
Group(cs):	S�ov�/D�moni
Group(da):	Netv�rks/D�moner
Group(de):	Netzwerkwesen/Server
Group(es):	Red/Servidores
Group(fr):	R�seau/Serveurs
Group(is):	Net/P�kar
Group(it):	Rete/Demoni
Group(no):	Nettverks/Daemoner
Group(pl):	Sieciowe/Serwery
Group(pt):	Rede/Servidores
Group(ru):	����/������
Group(sl):	Omre�ni/Stre�niki
Group(sv):	N�tverk/Demoner
Group(uk):	������/������
Source0:	ftp://ftp.sourceforge.net/pub/sourceforge/apantihak/mod_antihak-0.3.1-beta.tar.gz
Patch0:		mod_antihak-iptables.patch
Patch1:		mod_antihak-am.patch
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	apache(EAPI)-devel
BuildRequires:	libtool
BuildRequires:	mysql-devel
BuildRequires:	%{apxs}
Requires:	apache(EAPI) >= 1.3.1
Requires:	iptables
Requires:	sudo
Prereq:		%{_sbindir}/apxs
Prereq:		grep
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         _libexecdir     %{_libdir}/apache
%define         _htmldocdir     /home/httpd/manual/mod

%description
mod_antihak is an Apache Module designed to eliminate the CodeRed and
Nimda worm's network bandwidth consumption. We're working to make it
as easy as writing a line of text to add more worms! :)

%description -l pl
mod_antihak to modu� Apache s�u��cy do eliminowania zapychania sieci
przez robaki CodeRed i Nimda. Ponadto trwaj� prace nad umo�liwieniem
�atwego dodawania obs�ugi kolejnych robak�w.

%prep
%setup -q -n mod_antihak-0.3.1-beta
cd src
%patch0 -p0
%patch1 -p0

%build
cd src

rm -f tools/missing
libtoolize --copy --force
aclocal
autoconf
automake -a -c

%configure \
	CC=%{__cc} \
	CFLAGS="%{rpmcflags} -I/usr/include/mysql" \
	APACHE_APXS=%{apxs} \
	--with-mysql

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libexecdir},%{_htmldocdir}}

cd src

install mod_antihak/mod_antihak.so $RPM_BUILD_ROOT%{_libexecdir}

gzip -9nf AUTHORS INSTALL ChangeLog NEWS TODO

%post
if [ `fgrep "http ALL= NOPASSWD: /sbin/iptables" /etc/sudoers | wc -l` = 0 ] then
	echo "http ALL= NOPASSWD: /sbin/iptables" >> /etc/sudoers
fi

%{_sbindir}/apxs -e -a -n antihak %{_libexecdir}/mod_antihak.so 1>&2
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/httpd start\" to start apache http daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ `fgrep "http ALL= NOPASSWD: /sbin/iptables" /etc/sudoers | wc -l` != 0 ]
	then
		grep -v '^http ALL= NOPASSWD: /sbin/iptables$' /etc/sudoers \
			> /etc/sudoers.rpmnew-antihak
		mv -f /etc/sudoers.rpmnew-antihak /etc/sudoers
	fi

	%{_sbindir}/apxs -e -A -n antihak %{_libexecdir}/mod_antihak.so 1>&2
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc src/*.gz
%attr(755,root,root) %{_libexecdir}/*
