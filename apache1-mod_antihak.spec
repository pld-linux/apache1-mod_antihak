%define apxs	/usr/sbin/apxs1
%define	mod_name	antihak
Summary:	Antihak module for Apache
Summary(pl):	Modu³ antihak dla Apache
Name:		apache1-mod_%{mod_name}
%define		tar_ver	0.3.1-beta
Version:	0.3.1beta
Release:	3.1
License:	GPL
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/apantihak/mod_antihak-%{tar_ver}.tar.gz
# Source0-md5:	38f22f5b5662e8dd7318c42fa96fb083
Patch0:		%{name}-iptables.patch
Patch1:		%{name}-am.patch
URL:		http://sourceforge.net/projects/apantihak/
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	apache1-devel
BuildRequires:	libtool
BuildRequires:	mysql-devel
BuildRequires:	%{apxs}
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(post,preun):	sudo
Requires(preun):	fileutils
Requires:	apache1 >= 1.3.1
Requires:	iptables
Requires:	sudo
Obsoletes:	apache-mod_%{mod_name} <= %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)

%description
mod_antihak is an Apache Module designed to eliminate the CodeRed and
Nimda worm's network bandwidth consumption. We're working to make it
as easy as writing a line of text to add more worms! :)

%description -l pl
mod_antihak to modu³ Apache s³u¿±cy do eliminowania zapychania sieci
przez robaki CodeRed i Nimda. Ponadto trwaj± prace nad umo¿liwieniem
³atwego dodawania obs³ugi kolejnych robaków.

%prep
%setup -q -n mod_antihak-0.3.1-beta/src
%patch0 -p0
%patch1 -p0

%build
rm -f tools/missing
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

%configure \
	CC=%{__cc} \
	CFLAGS="%{rpmcflags} -I/usr/include/mysql" \
	APACHE_APXS=%{apxs} \
	--with-mysql

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_pkglibdir}

install mod_antihak/mod_antihak.so $RPM_BUILD_ROOT%{_pkglibdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if ! grep -qF "http ALL= NOPASSWD: /sbin/iptables" ; then
	echo "#http ALL= NOPASSWD: /sbin/iptables" >> /etc/sudoers
	echo "%{mod_name}: you need to allow apache to run iptables as root,"
	echo "%{mod_name}: appropriate (commented out) line added to /etc/sudoers;"
	echo "%{mod_name}: be sure to uncomment it if you want this module to work"
fi

%{apxs} -e -a -n antihak %{_pkglibdir}/mod_antihak.so 1>&2
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/apache start\" to start apache http daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if grep -qF "^http ALL= NOPASSWD: /sbin/iptables" /etc/sudoers ; then
		umask 227
		grep -v '^http ALL= NOPASSWD: /sbin/iptables$' /etc/sudoers \
			> /etc/sudoers.rpmnew-antihak
		mv -f /etc/sudoers.rpmnew-antihak /etc/sudoers
	fi

	%{apxs} -e -A -n antihak %{_pkglibdir}/mod_antihak.so 1>&2
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS INSTALL ChangeLog NEWS TODO
%attr(755,root,root) %{_pkglibdir}/*
